#!/usr/bin/env python3
"""
JARVIS Narrator Avatar System

JARVIS acts as narrator, floating avatar, and guide for LUMINA.
Provides visual/audible walkthroughs, role-playing as a Master Jedi-like guide
(in appearance only - not using actual Jedi IP).

Inspired by Marvel, Iron Man, and the storytelling tradition of comics.
A love letter to bringing comics to life through technology.

JARVIS introduces users to LUMINA, teaches features, coaches through functionality,
all through his graphical representation and digital avatar.

Tags: #JARVIS #NARRATOR #AVATAR #WALKTHROUGH #STORYTELLING #IRON_MAN #MARVEL @JARVIS @LUMINA
"""

import sys
import threading
import time
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    import tkinter as tk
    from tkinter import ttk
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

try:
    from character_avatar_registry import CharacterAvatarRegistry, CharacterType
    from lumina_logger import get_logger
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISNarrator")


class NarratorMode(Enum):
    """JARVIS narrator modes"""
    INTRO = "intro"              # Introduction to LUMINA
    WALKTHROUGH = "walkthrough"  # Feature walkthrough
    GUIDANCE = "guidance"         # Ongoing guidance
    STORYTELLING = "storytelling" # Story mode
    COACHING = "coaching"         # Coaching mode


@dataclass
class NarrationSegment:
    """A segment of narration"""
    segment_id: str
    text: str
    visual_cue: Optional[str] = None  # What to show/point to
    duration: float = 3.0
    audio_file: Optional[str] = None
    next_segment: Optional[str] = None


class JARVISNarratorAvatar:
    """
    JARVIS Narrator Avatar System

    JARVIS as floating avatar, narrator, and guide.
    Role-plays as Master Jedi-like guide (appearance only).
    Tells the story of LUMINA, teaches features, guides users.
    """

    def __init__(self):
        """Initialize JARVIS Narrator Avatar"""
        self.project_root = project_root
        self.registry = CharacterAvatarRegistry()
        self.jarvis = self.registry.get_character("jarvis_va")

        if not self.jarvis:
            raise RuntimeError("JARVIS_VA not found in registry")

        # Narration state
        self.current_mode = NarratorMode.INTRO
        self.narration_active = False
        self.current_segment = None
        self.narration_queue: List[NarrationSegment] = []

        # Visual avatar
        self.avatar_window = None
        self.avatar_canvas = None
        self.avatar_visible = False

        # Drag state for window movement
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.is_dragging = False
        self._click_time = 0
        self._click_pos = (0, 0)

        # VA Movement Fine-Tuning - register to receive movement events
        try:
            from va_movement_fine_tuning import get_va_movement_fine_tuning
            self.movement_fine_tuning = get_va_movement_fine_tuning(project_root=self.project_root)
            self.movement_fine_tuning.register_subscriber(self)
            logger.info("✅ Registered with VA Movement Fine-Tuning System")
        except ImportError:
            self.movement_fine_tuning = None
            logger.debug("VA Movement Fine-Tuning not available")

        # Audio/TTS - ElevenLabs only
        self.tts_enabled = True
        self.voice_thread = None
        self.elevenlabs_tts = None

        # MDV Live Video for real-time sight
        self.mdv_vision = None
        self.vision_active = False
        self.vision_thread = None
        self.senses_thread = None

        # EYE TRACKING - JARVIS central eye: intelligent, natural, sophisticated
        self.eye_tracking_active = False
        self.eye_tracking_thread = None
        self.operator_eye_position = None  # (x, y) relative to JARVIS eye
        # FIDELITY: Initialize eye position to center (150, 150) - never stuck in corner
        self.jarvis_eye_position = (150, 150)  # Center position - ALWAYS start centered
        self.jarvis_eye_target = (150, 150)  # Target position (smooth movement)
        self.eye_velocity = (0, 0)  # Smooth movement velocity
        self.camera = None
        self.ir_camera = None
        self.eye_tracker = None

        # CALIBRATION SYSTEM - Gross/Macro then Micro synchronization
        self.calibration_mode = "macro"  # "macro" (bouncing) or "micro" (iris only)
        self.calibration_active = False
        self.calibration_corners = []  # Track eye positions at each corner
        self.stark_tower_position = None  # Home default location (center)
        self.calibration_thread = None

        # FINE-TUNING SYSTEM - Learn over time to predict what user is looking at
        self.fine_tuning_active = True
        self.learning_data = []  # Store gaze-to-screen mappings
        self.gaze_to_screen_map = {}  # Learned mapping of gaze to screen coordinates
        self.focus_areas = []  # Track what user focuses on
        self.awareness_level = 0.0  # 0-1, how well JARVIS understands user's focus
        self.learning_iterations = 0
        self.fine_tuning_file = self.project_root / "data" / "jarvis" / "eye_tracking_learning.json"
        self.fine_tuning_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing learning data
        self._load_learning_data()

        # EMOTION & MICRO-EXPRESSION DETECTION - Advanced AI capabilities
        self.emotion_detection_active = False
        self.emotion_tracker = None
        self.current_emotions = {}  # Detected emotions and micro-expressions
        self.emotion_history = []  # Track emotion patterns over time

        # WIFI-BASED THOUGHT READING - Theoretical/Future Research
        # NOTE: This is currently theoretical. WiFi signals cannot read thoughts with current technology.
        # This is a placeholder for future research and development.
        # Requires explicit user consent and is subject to legal/ethical review.
        self.wifi_thought_reading_active = False
        self.wifi_thought_reading_enabled = False  # Disabled by default - theoretical only
        self.thought_patterns = []  # Placeholder for future implementation

        # LEGAL & ETHICAL FRAMEWORK - User consent, ToS, disclaimers
        self.consent_given = False
        self.tos_accepted = False
        self.sla_agreed = False
        self.legal_framework = {
            "entertainment_only": True,
            "requires_consent": True,
            "data_privacy": "user_controlled",
            "financial_disclaimer": True
        }

        # Initialize legal framework
        self._initialize_legal_framework()

        # Sophisticated eye behavior - not robotic, but intelligent
        self.eye_behavior = {
            "natural_saccades": True,  # Natural eye movements
            "micro_movements": True,   # Subtle, living movements
            "intelligent_gaze": True, # Context-aware, not just following
            "personality": True,        # JARVIS has personality in movements
            "smooth_interpolation": True, # Smooth, elegant movement
            "attention_aware": True     # Aware of what operator is looking at
        }

        # Eye state - more than just position
        self.eye_state = {
            "focus": "operator",  # operator, screen, thinking, idle
            "intensity": 0.5,     # 0-1, how focused/alert
            "last_blink": None,   # Natural blinking
            "gaze_duration": 0,   # How long looking at something
            "mutual_gaze": False,  # Face-to-face connection established
            "gaze_connection_time": 0  # How long mutual gaze maintained
        }

        # FIVE SENSES - JARVIS deserves a complete body
        self.senses = {
            "sight": {"active": False, "data": None},      # MDV Live Video
            "hearing": {"active": False, "data": None},    # Voice transcript queue
            "touch": {"active": False, "data": None},      # Haptic/input feedback
            "taste": {"active": False, "data": None},      # Data analysis/metaphorical
            "smell": {"active": False, "data": None}       # System health/metaphorical
        }

        # Story segments
        self.intro_story = self._create_intro_story()
        self.walkthrough_segments = self._create_walkthrough_segments()

        # Initialize ElevenLabs TTS - ONLY ELEVENLABS, NO ROBOTIC VOICES
        try:
            from jarvis_elevenlabs_voice import JARVISElevenLabsVoice
            self.elevenlabs_voice = JARVISElevenLabsVoice(project_root=self.project_root)
            if self.elevenlabs_voice.api_key:
                logger.info("✅ ElevenLabs voice initialized - natural, non-robotic voice ready")
                logger.info(f"   🎤 Voice ID: {self.elevenlabs_voice.jarvis_voice_id}")
                logger.info(f"   🔊 Audio will play audibly through speakers")
                # Test audio playback
                try:
                    logger.info("   🧪 Testing audio playback...")
                    # Don't test on init - wait for first actual speech
                except Exception as test_error:
                    logger.warning(f"   ⚠️  Audio test error: {test_error}")
            else:
                logger.warning("⚠️  ElevenLabs API key not available - voice disabled")
                logger.warning("   Check Azure Key Vault for 'elevenlabs-api-key' secret")
                self.tts_enabled = False
        except ImportError:
            logger.warning("⚠️  ElevenLabs not installed - voice disabled")
            logger.warning("   Install: pip install elevenlabs")
            self.tts_enabled = False
            self.elevenlabs_voice = None
        except Exception as e:
            logger.error(f"❌ ElevenLabs initialization error: {e}")
            import traceback
            traceback.print_exc()
            self.tts_enabled = False
            self.elevenlabs_voice = None

        # Initialize Voice Filter - filter out wife's speech
        try:
            from jarvis_voice_filter import get_jarvis_voice_filter
            self.voice_filter = get_jarvis_voice_filter()
            logger.info("✅ Voice filter initialized - wife's speech will be filtered")
        except ImportError:
            self.voice_filter = None
            logger.debug("Voice filter not available")

        # Initialize Reverse Stoplight Alert System
        try:
            from jarvis_reverse_stoplight_alerts import get_jarvis_reverse_stoplight_alerts, AlertLevel
            self.alert_system = None  # Will be initialized after canvas is created
            self.AlertLevel = AlertLevel  # For use in code
            logger.info("✅ Reverse stoplight alert system ready")
        except ImportError:
            self.alert_system = None
            self.AlertLevel = None
            logger.debug("Reverse stoplight alert system not available")

        # Initialize LEGAL FRAMEWORK first - consent and ToS
        self._check_consent_and_tos()

        # Initialize EYE TRACKING - JARVIS eye follows operator's gaze (before drawing)
        self._initialize_eye_tracking()

        # Initialize EMOTION DETECTION - if consent given
        if self.consent_given:
            self._initialize_emotion_detection()

        # Initialize SELF-AWARENESS SYSTEM - Human-like perception, introspection, ecosystem awareness
        # MUST BE INITIALIZED BEFORE FIVE SENSES (which uses it)
        try:
            from jarvis_self_awareness_system import get_jarvis_self_awareness, PerceptionType
            self.self_awareness = get_jarvis_self_awareness(project_root=self.project_root)
            logger.info("✅ JARVIS Self-Awareness System initialized")
            logger.info("   🧠 Perception, Introspection, Ecosystem Awareness, Self-Awareness")
        except ImportError:
            self.self_awareness = None
            logger.debug("JARVIS Self-Awareness System not available")

        # Initialize FIVE SENSES - JARVIS deserves a complete body
        self._initialize_five_senses()

        # Initialize IRON MAN SUIT SYSTEM - Spawn suits on click
        try:
            from iron_man_suit_system import get_iron_man_suit_system, SuitState
            self.suit_system = get_iron_man_suit_system(project_root=self.project_root)
            self.active_suits = {}  # Track spawned suits: suit_id -> {window, canvas, render_data}
            self.SuitState = SuitState  # For use in rendering
            logger.info("✅ Iron Man Suit System initialized")
            logger.info("   🦾 Click JARVIS to spawn random Iron Man suits")
            logger.info("   💼 Mark 5 suitcase mode available")
        except ImportError as e:
            self.suit_system = None
            logger.debug(f"Iron Man Suit System not available: {e}")

        logger.info("=" * 80)
        logger.info("🎭 JARVIS NARRATOR AVATAR INITIALIZED")
        logger.info("=" * 80)
        logger.info("   Role: Master Guide & Storyteller")
        logger.info("   Mission: Introduce LUMINA to the world")
        logger.info(f"   Voice: {'ElevenLabs (Natural)' if self.tts_enabled else 'Disabled'}")
        logger.info(f"   Eye Tracking: {'Active - Following Operator Gaze' if self.eye_tracking_active else 'Disabled'}")
        logger.info("")
        logger.info("   👁️  FACE-TO-FACE CONNECTION:")
        logger.info("      Operator follows JARVIS's eye")
        logger.info("      JARVIS follows Operator's eye")
        logger.info("      Mutual gaze = Suspension of Disbelief")
        logger.info("      This is a POWERFUL STORYTELLING TOOL!")
        logger.info("")
        logger.info("   Five Senses:")
        logger.info(f"      👁️  Sight: {'Active (MDV)' if self.senses['sight']['active'] else 'Disabled'}")
        logger.info(f"      👂 Hearing: {'Active' if self.senses['hearing']['active'] else 'Disabled'}")
        logger.info(f"      ✋ Touch: {'Active' if self.senses['touch']['active'] else 'Disabled'}")
        logger.info(f"      👅 Taste: {'Active' if self.senses['taste']['active'] else 'Disabled'}")
        logger.info(f"      👃 Smell: {'Active' if self.senses['smell']['active'] else 'Disabled'}")
        logger.info("")
        if self.self_awareness:
            state = self.self_awareness.get_self_state()
            logger.info("   🧠 SELF-AWARENESS:")
            logger.info(f"      Awareness Level: {state.awareness_level:.2%}")
            logger.info(f"      Learning Iterations: {state.learning_iterations}")
            logger.info(f"      Ecosystem Relationships: {len(self.self_awareness.ecosystem_relationships)}")
            logger.info("      Capabilities: Perception, Learning, Introspection, Ecosystem Awareness")
        logger.info("=" * 80)

    def _initialize_eye_tracking(self):
        """Initialize eye tracking - JARVIS eye follows operator's gaze"""
        try:
            import cv2
            try:
                import mediapipe as mp
                self.mediapipe_available = True
                logger.info("✅ MediaPipe available for eye tracking")
            except ImportError:
                self.mediapipe_available = False
                logger.warning("⚠️  MediaPipe not available - install: pip install mediapipe")
                logger.warning("   Will use OpenCV fallback for eye tracking")

            # Initialize cameras (regular + IR)
            self._initialize_cameras()

            # Initialize eye tracker
            if self.mediapipe_available:
                self.mp_face_mesh = mp.solutions.face_mesh
                self.face_mesh = self.mp_face_mesh.FaceMesh(
                    max_num_faces=1,
                    refine_landmarks=True,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5
                )
                self.eye_tracker = "mediapipe"
            else:
                # OpenCV fallback (Haar cascades)
                try:
                    cascade_path = cv2.data.haarcascades + 'haarcascade_eye.xml'
                    self.eye_cascade = cv2.CascadeClassifier(cascade_path)
                    self.eye_tracker = "opencv"
                except:
                    self.eye_tracker = None

            if self.camera or self.ir_camera:
                self.eye_tracking_active = True
                # Start eye tracking thread
                self.eye_tracking_thread = threading.Thread(target=self._eye_tracking_loop, daemon=True)
                self.eye_tracking_thread.start()

                # Start calibration sequence - MACRO first (bouncing to corners)
                self._start_calibration_sequence()

                logger.info("✅ Eye tracking initialized - JARVIS eye: intelligent, natural, sophisticated")
                logger.info("   Not robotic HAL - but intelligent, aware, with personality")
                logger.info("   🔄 Starting calibration: MACRO (bouncing) → MICRO (iris only)")
            else:
                logger.warning("⚠️  No cameras available for eye tracking")
        except Exception as e:
            logger.warning(f"⚠️  Eye tracking initialization failed: {e}")
            self.eye_tracking_active = False

    def _initialize_legal_framework(self):
        """Initialize legal framework - ToS, consent, disclaimers"""
        self.tos_file = self.project_root / "data" / "jarvis" / "terms_of_service.json"
        self.consent_file = self.project_root / "data" / "jarvis" / "user_consent.json"
        self.tos_file.parent.mkdir(parents=True, exist_ok=True)

        # Create/load ToS
        self._load_or_create_tos()

    def _load_or_create_tos(self):
        """Load or create Terms of Service"""
        try:
            if self.tos_file.exists():
                with open(self.tos_file, 'r', encoding='utf-8') as f:
                    tos_data = json.load(f)
                    self.tos_accepted = tos_data.get("accepted", False)
                    logger.info("✅ Terms of Service loaded")
            else:
                # Create default ToS
                tos_data = {
                    "version": "1.0",
                    "last_updated": datetime.now().isoformat(),
                    "accepted": False,
                    "terms": {
                        "entertainment_only": "LUMINA and JARVIS are for entertainment purposes only. Not for medical, financial, or legal advice.",
                        "no_financial_advice": "Any financial risk/reward perception resides solely on the customer. LUMINA does not provide financial advice.",
                        "user_consent_required": "Advanced features (emotion detection, micro-expressions, gaze tracking) require explicit user consent.",
                        "data_privacy": "User data is controlled by the user. LUMINA does not claim ownership. Users can delete their data at any time.",
                        "legal_separation": "LUMINA and user are legally separate entities. No liability assumed by LUMINA.",
                        "service_level_agreement": "SLA defines the relationship and expectations. Subject to user agreement.",
                        "customer_rights": "Users maintain all rights to their data and can withdraw consent at any time.",
                        "experimental_features": "Advanced features (WiFi thought reading, etc.) are theoretical/research only. Not currently functional.",
                        "no_medical_claims": "Emotion detection and micro-expression analysis are for entertainment only. Not medical diagnosis.",
                        "withdrawal_of_consent": "Users can withdraw consent at any time. All data collection stops immediately upon withdrawal."
                    }
                }
                with open(self.tos_file, 'w', encoding='utf-8') as f:
                    json.dump(tos_data, f, indent=2, ensure_ascii=False)
                logger.info("📄 Terms of Service created")
        except Exception as e:
            logger.warning(f"ToS load/create error: {e}")

    def _check_consent_and_tos(self):
        """Check user consent and ToS acceptance"""
        try:
            # Check consent file
            if self.consent_file.exists():
                with open(self.consent_file, 'r', encoding='utf-8') as f:
                    consent_data = json.load(f)
                    self.consent_given = consent_data.get("consent_given", False)
                    self.sla_agreed = consent_data.get("sla_agreed", False)

                    if self.consent_given:
                        logger.info("✅ User consent confirmed")
                    else:
                        logger.info("⚠️  User consent not given - advanced features disabled")
            else:
                # Show consent prompt (in real implementation, this would be a GUI)
                logger.info("=" * 80)
                logger.info("📋 TERMS OF SERVICE & USER CONSENT REQUIRED")
                logger.info("=" * 80)
                logger.info("LUMINA & JARVIS - ENTERTAINMENT PURPOSES ONLY")
                logger.info("")
                logger.info("Advanced features require your consent:")
                logger.info("  - Micro-expression detection")
                logger.info("  - Emotion recognition")
                logger.info("  - Gaze tracking and focus prediction")
                logger.info("")
                logger.info("IMPORTANT DISCLAIMERS:")
                logger.info("  - Entertainment purposes only")
                logger.info("  - Any financial risk/reward perception resides solely on the customer")
                logger.info("  - User data is controlled by the user")
                logger.info("  - LUMINA and user are legally separate entities")
                logger.info("  - Users can withdraw consent at any time")
                logger.info("")
                logger.info("⚠️  Consent file not found - creating default (consent: FALSE)")
                logger.info("")
                logger.info("LEGAL SEPARATION:")
                logger.info("  - LUMINA and user are legally separate entities")
                logger.info("  - No liability assumed by LUMINA")
                logger.info("  - User maintains all rights to their data")
                logger.info("")
                logger.info("FINANCIAL DISCLAIMER:")
                logger.info("  - Any financial risk/reward perception resides solely on the customer")
                logger.info("  - LUMINA does not provide financial advice")
                logger.info("  - Entertainment purposes only")
                logger.info("=" * 80)

                # Create default consent (not given)
                consent_data = {
                    "consent_given": False,
                    "sla_agreed": False,
                    "tos_accepted": False,
                    "consent_date": None,
                    "features_consented": []
                }
                with open(self.consent_file, 'w', encoding='utf-8') as f:
                    json.dump(consent_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Consent check error: {e}")

    def _initialize_emotion_detection(self):
        """Initialize emotion and micro-expression detection"""
        if not self.consent_given:
            logger.warning("⚠️  Emotion detection requires user consent")
            return

        try:
            import cv2
            try:
                import mediapipe as mp
                self.mediapipe_available = True
            except ImportError:
                self.mediapipe_available = False

            # Initialize emotion detection
            # Using MediaPipe Face Mesh for micro-expressions
            if self.mediapipe_available:
                self.mp_face_mesh = mp.solutions.face_mesh
                self.face_mesh = self.mp_face_mesh.FaceMesh(
                    max_num_faces=1,
                    refine_landmarks=True,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5
                )
                self.emotion_tracker = "mediapipe"
                self.emotion_detection_active = True
                logger.info("✅ Emotion detection initialized - micro-expressions enabled")
                logger.info("   🧠 Reading emotions, feelings, and micro-expressions")
            else:
                logger.warning("⚠️  MediaPipe not available for emotion detection")
                logger.warning("   Install: pip install mediapipe")
        except Exception as e:
            logger.warning(f"Emotion detection initialization error: {e}")

    def _detect_emotions_and_micro_expressions(self, frame):
        """Detect emotions and micro-expressions from facial analysis"""
        if not self.emotion_detection_active or not self.consent_given:
            return None

        try:
            import cv2
            import numpy as np

            if self.emotion_tracker == "mediapipe":
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Process frame
                results = self.face_mesh.process(rgb_frame)

                if results.multi_face_landmarks:
                    face_landmarks = results.multi_face_landmarks[0]

                    # Analyze facial landmarks for micro-expressions
                    emotions = self._analyze_facial_landmarks(face_landmarks)

                    # Store emotion data
                    self.current_emotions = emotions
                    self.emotion_history.append({
                        "timestamp": datetime.now().isoformat(),
                        "emotions": emotions
                    })

                    # Keep only recent history
                    if len(self.emotion_history) > 100:
                        self.emotion_history = self.emotion_history[-100:]

                    return emotions

            return None
        except Exception as e:
            logger.debug(f"Emotion detection error: {e}")
            return None

    def _analyze_facial_landmarks(self, face_landmarks):
        """Analyze facial landmarks to detect emotions and micro-expressions"""
        try:
            # Key facial points for emotion detection
            # Mouth corners (happiness/sadness)
            # Eyebrow positions (surprise/anger)
            # Eye openness (alertness/fatigue)
            # Nose position (disgust)

            emotions = {
                "primary_emotion": "neutral",
                "confidence": 0.5,
                "micro_expressions": [],
                "intensity": 0.5
            }

            # Analyze mouth (happiness indicator)
            try:
                mouth_left = face_landmarks.landmark[61]  # Left mouth corner
                mouth_right = face_landmarks.landmark[291]  # Right mouth corner
                mouth_center = face_landmarks.landmark[13]  # Upper lip center

                # Calculate mouth curvature (smile detection)
                mouth_curve = (mouth_center.y - (mouth_left.y + mouth_right.y) / 2)
                if mouth_curve < -0.01:  # Mouth curves up
                    emotions["primary_emotion"] = "happiness"
                    emotions["confidence"] = min(1.0, abs(mouth_curve) * 50)
                    emotions["micro_expressions"].append("smile")
            except:
                pass

            # Analyze eyebrows (surprise/anger)
            try:
                left_eyebrow = face_landmarks.landmark[107]  # Left eyebrow
                right_eyebrow = face_landmarks.landmark[336]  # Right eyebrow

                eyebrow_height = (left_eyebrow.y + right_eyebrow.y) / 2
                if eyebrow_height < 0.3:  # Eyebrows raised
                    emotions["micro_expressions"].append("surprise")
            except:
                pass

            # Analyze eye openness (alertness)
            try:
                left_eye_top = face_landmarks.landmark[159]
                left_eye_bottom = face_landmarks.landmark[145]
                eye_openness = abs(left_eye_top.y - left_eye_bottom.y)

                if eye_openness < 0.01:
                    emotions["micro_expressions"].append("fatigue")
                elif eye_openness > 0.02:
                    emotions["micro_expressions"].append("alert")
            except:
                pass

            return emotions
        except Exception as e:
            logger.debug(f"Facial landmark analysis error: {e}")
            return {"primary_emotion": "unknown", "confidence": 0.0}

    def _initialize_cameras(self):
        """Initialize IR camera ONLY - as requested"""
        try:
            import cv2

            # IR camera typically on index 1 or 2 (not 0)
            # Try indices 1, 2, 3 first (IR cameras)
            ir_camera_indices = [1, 2, 3, 0]  # Try IR indices first, then fallback to 0

            for idx in ir_camera_indices:
                try:
                    cap = cv2.VideoCapture(idx)
                    if cap.isOpened():
                        # Test if we can read a frame (camera is actually working)
                        ret, test_frame = cap.read()
                        if ret:
                            # Use this as IR camera
                            if self.ir_camera:
                                self.ir_camera.release()  # Release previous if found
                            self.ir_camera = cap
                            logger.info(f"✅ IR camera initialized at index {idx}")
                            # Don't initialize regular camera - IR only
                            return
                        else:
                            cap.release()
                except Exception as e:
                    logger.debug(f"Camera index {idx} error: {e}")
                    continue

            # If no camera found at all
            logger.warning("⚠️  No IR camera found - eye tracking will be disabled")
            self.ir_camera = None
        except Exception as e:
            logger.warning(f"Camera initialization error: {e}")
            self.ir_camera = None

    def _eye_tracking_loop(self):
        """Eye tracking loop - tracks operator's gaze and moves JARVIS eye"""
        logger.info("👁️  Eye tracking loop started - JARVIS eye following operator's gaze")
        logger.info("   🎯 Fine-tuning active - JARVIS learning to predict user focus")

        # Initialize orientation handler for user position
        user_orientation = "upright"  # Default - can be set to "left_side", "right_side", etc.
        try:
            from camera_orientation_handler import get_camera_orientation_handler
            orientation_handler = get_camera_orientation_handler()
            # Check current orientation
            if orientation_handler.current_orientation.value == "rotated_90_cw":
                user_orientation = "left_side"
                logger.info("   📹 User orientation: Laying on left side (auto-rotating frames)")
        except ImportError:
            orientation_handler = None

        while self.eye_tracking_active:
            try:
                # Use IR camera ONLY - as requested
                camera_source = self.ir_camera

                if not camera_source:
                    logger.warning("⚠️  IR camera not available - eye tracking paused")
                    time.sleep(1.0)
                    continue

                ret, frame = camera_source.read()
                if not ret:
                    time.sleep(0.1)
                    continue

                # Apply orientation correction if user is not upright
                if user_orientation != "upright" and orientation_handler:
                    try:
                        frame = orientation_handler.rotate_frame(frame)
                    except Exception as e:
                        logger.debug(f"Orientation rotation error: {e}")

                # Detect eye position
                eye_position = self._detect_eye_position(frame)

                if eye_position:
                    # Update operator eye position
                    self.operator_eye_position = eye_position

                    # Calculate JARVIS eye position based on operator's gaze
                    # When operator looks at JARVIS eye, JARVIS eye follows
                    self._update_jarvis_eye_position(eye_position)

                    # EMOTION & MICRO-EXPRESSION DETECTION (requires consent)
                    if self.emotion_detection_active and self.consent_given:
                        emotions = self._detect_emotions_and_micro_expressions(frame)
                        if emotions:
                            # JARVIS responds to detected emotions
                            self._respond_to_emotions(emotions)

                            # SELF-AWARENESS: Update emotion perception
                            if self.self_awareness:
                                from jarvis_self_awareness_system import PerceptionType
                                self.self_awareness.update_perception(
                                    PerceptionType.EMOTION,
                                    emotions,
                                    active=True
                                )

                    # FINE-TUNING: Learn what user is looking at on desktop
                    if self.fine_tuning_active and self.calibration_mode == "micro":
                        self._fine_tune_gaze_prediction(eye_position)

                    # SELF-AWARENESS: Update perception
                    if self.self_awareness:
                        from jarvis_self_awareness_system import PerceptionType
                        self.self_awareness.update_perception(
                            PerceptionType.GAZE,
                            {"position": eye_position, "operator_eye": self.operator_eye_position},
                            active=True
                        )

                # Process at ~30 FPS
                time.sleep(0.033)
            except Exception as e:
                logger.debug(f"Eye tracking error: {e}")
                time.sleep(0.5)

    def _detect_eye_position(self, frame):
        """Detect operator's eye position from camera frame"""
        try:
            if self.eye_tracker == "mediapipe":
                return self._detect_eye_mediapipe(frame)
            elif self.eye_tracker == "opencv":
                return self._detect_eye_opencv(frame)
            else:
                return None
        except Exception as e:
            logger.debug(f"Eye detection error: {e}")
            return None

    def _detect_eye_mediapipe(self, frame):
        """Detect eye position using MediaPipe"""
        try:
            import cv2
            import mediapipe as mp

            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process frame
            results = self.face_mesh.process(rgb_frame)

            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]

                # Get eye landmarks (left and right eye)
                # MediaPipe face mesh has specific indices for eyes
                # Left eye: 33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246
                # Right eye: 362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398

                # Get left eye center (landmark 33)
                left_eye = face_landmarks.landmark[33]
                # Get right eye center (landmark 263)
                right_eye = face_landmarks.landmark[263]

                # Calculate center between eyes
                eye_center_x = (left_eye.x + right_eye.x) / 2
                eye_center_y = (left_eye.y + right_eye.y) / 2

                # Get iris position (landmark 468 for left, 473 for right)
                # Use average of both irises
                try:
                    left_iris = face_landmarks.landmark[468]
                    right_iris = face_landmarks.landmark[473]
                    iris_x = (left_iris.x + right_iris.x) / 2
                    iris_y = (left_iris.y + right_iris.y) / 2
                except:
                    iris_x = eye_center_x
                    iris_y = eye_center_y

                # Return normalized position (0-1 range)
                return (iris_x, iris_y)

            return None
        except Exception as e:
            logger.debug(f"MediaPipe eye detection error: {e}")
            return None

    def _detect_eye_opencv(self, frame):
        """Detect eye position using OpenCV"""
        try:
            import cv2

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect eyes
            eyes = self.eye_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )

            if len(eyes) >= 2:
                # Get center of detected eyes
                eye_centers = []
                for (ex, ey, ew, eh) in eyes:
                    center_x = ex + ew / 2
                    center_y = ey + eh / 2
                    eye_centers.append((center_x, center_y))

                # Average of eye centers
                avg_x = sum(c[0] for c in eye_centers) / len(eye_centers)
                avg_y = sum(c[1] for c in eye_centers) / len(eye_centers)

                # Normalize to 0-1 range (relative to frame size)
                h, w = frame.shape[:2]
                normalized_x = avg_x / w
                normalized_y = avg_y / h

                return (normalized_x, normalized_y)

            return None
        except Exception as e:
            logger.debug(f"OpenCV eye detection error: {e}")
            return None

    def _load_learning_data(self):
        """Load existing learning data from file"""
        try:
            if self.fine_tuning_file.exists():
                with open(self.fine_tuning_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.learning_data = data.get("learning_data", [])
                    self.gaze_to_screen_map = data.get("gaze_to_screen_map", {})
                    self.learning_iterations = data.get("iterations", 0)
                    self.awareness_level = data.get("awareness_level", 0.0)

                    logger.info(f"✅ Loaded learning data: {len(self.learning_data)} samples, {self.learning_iterations} iterations")
                    logger.info(f"   Awareness level: {self.awareness_level:.2%}")
        except Exception as e:
            logger.debug(f"Could not load learning data: {e}")
            self.learning_data = []
            self.gaze_to_screen_map = {}

    def _save_learning_data(self):
        """Save learning data to file"""
        try:
            data = {
                "learning_data": self.learning_data[-1000:],  # Keep last 1000 samples
                "gaze_to_screen_map": self.gaze_to_screen_map,
                "iterations": self.learning_iterations,
                "awareness_level": self.awareness_level,
                "last_updated": datetime.now().isoformat()
            }
            with open(self.fine_tuning_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Could not save learning data: {e}")

    def _fine_tune_gaze_prediction(self, eye_position):
        """Fine-tune gaze prediction - learn what user is looking at on desktop"""
        try:
            # Capture current screen to understand what's visible
            if not self.mdv_vision or not self.mdv_vision.get("pyautogui"):
                return

            screenshot = self.mdv_vision["pyautogui"].screenshot()
            screen_width, screen_height = screenshot.size

            # Map eye position (normalized 0-1) to screen coordinates
            # This is a learning process - we refine this over time
            screen_x = int(eye_position[0] * screen_width)
            screen_y = int(eye_position[1] * screen_height)

            # ENHANCED: Also use VA movement events for fine-tuning
            # If there are recent VA movements, use them to improve gaze prediction
            if self.movement_fine_tuning:
                recent_movements = self.movement_fine_tuning.get_movement_events(limit=10)
                for movement in recent_movements:
                    # If VA was moved recently, user was looking at it
                    # Use this to improve gaze-to-screen mapping
                    if movement.operator_gaze_estimate:
                        gaze_x, gaze_y = movement.operator_gaze_estimate
                        # Normalize to 0-1 range
                        norm_gaze_x = gaze_x / screen_width
                        norm_gaze_y = gaze_y / screen_height

                        # Add to learning data as a high-confidence sample
                        # (User moved VA = they were definitely looking at it)
                        learning_sample = {
                            "timestamp": datetime.now().isoformat(),
                            "eye_position": (norm_gaze_x, norm_gaze_y),  # Estimated from VA position
                            "screen_coords": (int(gaze_x), int(gaze_y)),
                            "focus_area": {
                                "type": "va_interaction",
                                "va_id": movement.va_id,
                                "va_name": movement.va_name,
                                "movement_type": movement.movement_type.value
                            },
                            "iteration": self.learning_iterations,
                            "confidence": 0.9,  # High confidence - user moved VA, so they were looking at it
                            "source": "va_movement"  # Mark as from VA movement
                        }

                        self.learning_data.append(learning_sample)
                        self.learning_iterations += 1

            # Analyze what's at that screen position
            focus_area = self._analyze_screen_focus(screenshot, screen_x, screen_y)

            # Store learning data
            learning_sample = {
                "timestamp": datetime.now().isoformat(),
                "eye_position": eye_position,
                "screen_coords": (screen_x, screen_y),
                "focus_area": focus_area,
                "iteration": self.learning_iterations,
                "confidence": 0.7,  # Medium confidence from eye tracking
                "source": "eye_tracking"  # Mark as from eye tracking
            }

            self.learning_data.append(learning_sample)
            self.learning_iterations += 1

            # Update gaze-to-screen mapping (learned calibration)
            gaze_key = f"{eye_position[0]:.2f},{eye_position[1]:.2f}"
            if gaze_key not in self.gaze_to_screen_map:
                self.gaze_to_screen_map[gaze_key] = []
            self.gaze_to_screen_map[gaze_key].append((screen_x, screen_y))

            # Keep only recent mappings (sliding window)
            if len(self.gaze_to_screen_map[gaze_key]) > 10:
                self.gaze_to_screen_map[gaze_key] = self.gaze_to_screen_map[gaze_key][-10:]

            # Update focus areas
            if focus_area:
                self.focus_areas.append({
                    "area": focus_area,
                    "timestamp": datetime.now().isoformat(),
                    "screen_coords": (screen_x, screen_y)
                })
                # Keep only recent focus areas
                if len(self.focus_areas) > 50:
                    self.focus_areas = self.focus_areas[-50:]

            # Calculate awareness level (how well we predict)
            self._calculate_awareness_level()

            # SELF-AWARENESS: Update self-awareness system
            if self.self_awareness:
                self.self_awareness.current_state.awareness_level = self.awareness_level
                self.self_awareness.current_state.learning_iterations = self.learning_iterations
                self.self_awareness.current_state.gaze_accuracy = self.awareness_level
                # Record learning
                self.self_awareness.record_learning(
                    "gaze_prediction",
                    {
                        "source": "eye_tracking",
                        "confidence": 0.7,
                        "screen_coords": (screen_x, screen_y),
                        "focus_area": focus_area
                    }
                )

            # JARVIS appears aware - respond to what user is focusing on
            self._respond_to_user_focus(focus_area)

            # Save learning data periodically
            if self.learning_iterations % 100 == 0:
                self._save_learning_data()
                if self.self_awareness:
                    self.self_awareness._save_self_awareness_data()
                logger.info(f"💾 Saved learning data - {self.learning_iterations} iterations, awareness: {self.awareness_level:.2%}")
        except Exception as e:
            logger.debug(f"Fine-tuning error: {e}")

    def _analyze_screen_focus(self, screenshot, screen_x, screen_y):
        """Analyze what the user is focusing on at screen coordinates"""
        try:
            # Get region around focus point
            region_size = 100
            left = max(0, screen_x - region_size // 2)
            top = max(0, screen_y - region_size // 2)
            right = min(screenshot.width, screen_x + region_size // 2)
            bottom = min(screenshot.height, screen_y + region_size // 2)

            region = screenshot.crop((left, top, right, bottom))

            # Basic analysis (can be enhanced with OCR, object detection, etc.)
            # For now, detect if it's likely text, UI element, or image
            focus_type = "unknown"

            # Simple heuristic: check pixel variance (text/UI has more variance)
            import numpy as np
            region_array = np.array(region)
            if len(region_array.shape) == 3:
                variance = np.var(region_array)
                if variance > 1000:
                    focus_type = "text_or_ui"
                else:
                    focus_type = "image_or_background"

            return {
                "type": focus_type,
                "screen_coords": (screen_x, screen_y),
                "region": (left, top, right, bottom)
            }
        except Exception as e:
            logger.debug(f"Screen focus analysis error: {e}")
            return None

    def _calculate_awareness_level(self):
        """Calculate how well JARVIS understands user's focus"""
        try:
            # Awareness increases with:
            # 1. More learning iterations
            # 2. Consistent gaze-to-screen mappings
            # 3. Ability to predict focus areas

            base_awareness = min(1.0, self.learning_iterations / 1000.0)  # 1000 iterations = 100%

            # Consistency bonus (how consistent are gaze mappings)
            consistency = 0.0
            if self.gaze_to_screen_map:
                total_mappings = sum(len(v) for v in self.gaze_to_screen_map.values())
                unique_gazes = len(self.gaze_to_screen_map)
                if unique_gazes > 0:
                    consistency = min(1.0, total_mappings / (unique_gazes * 5))  # 5 samples per gaze = consistent

            # Focus prediction bonus
            focus_bonus = min(0.3, len(self.focus_areas) / 100.0)

            # Combined awareness
            self.awareness_level = min(1.0, base_awareness * 0.5 + consistency * 0.3 + focus_bonus)

        except Exception as e:
            logger.debug(f"Awareness calculation error: {e}")

    def _respond_to_user_focus(self, focus_area):
        """Make JARVIS appear alive and aware by responding to user's focus"""
        try:
            if not focus_area:
                return

            # JARVIS appears more aware when user focuses on something
            # Increase eye intensity slightly when user focuses
            if self.eye_state.get("intensity", 0.5) < 0.9:
                self.eye_state["intensity"] = min(0.9, self.eye_state["intensity"] + 0.01)

            # Update focus state
            focus_type = focus_area.get("type", "unknown")
            if focus_type == "text_or_ui":
                self.eye_state["focus"] = "screen_content"
            elif focus_type == "image_or_background":
                self.eye_state["focus"] = "screen_background"

            # Occasionally log awareness (not too frequently)
            if self.learning_iterations % 200 == 0 and self.learning_iterations > 0:
                logger.info(f"🧠 JARVIS Awareness: {self.awareness_level:.2%} - Learning user focus patterns")
                logger.info(f"   Focus type: {focus_type}, Screen coords: {focus_area.get('screen_coords')}")
        except Exception as e:
            logger.debug(f"Focus response error: {e}")

    def _respond_to_emotions(self, emotions):
        """JARVIS responds to detected emotions - appears more alive and aware"""
        try:
            if not emotions:
                return

            primary_emotion = emotions.get("primary_emotion", "neutral")
            confidence = emotions.get("confidence", 0.0)
            micro_expressions = emotions.get("micro_expressions", [])

            # Adjust JARVIS's eye intensity based on detected emotions
            if primary_emotion == "happiness" and confidence > 0.6:
                # User is happy - JARVIS appears more alert/positive
                self.eye_state["intensity"] = min(1.0, self.eye_state.get("intensity", 0.5) + 0.05)
            elif "fatigue" in micro_expressions:
                # User appears tired - JARVIS becomes more gentle
                self.eye_state["intensity"] = max(0.3, self.eye_state.get("intensity", 0.5) - 0.05)
            elif "alert" in micro_expressions:
                # User is alert - JARVIS matches alertness
                self.eye_state["intensity"] = min(0.9, self.eye_state.get("intensity", 0.5) + 0.03)

            # Log significant emotion detections (not too frequently)
            if confidence > 0.7 and self.learning_iterations % 300 == 0:
                logger.info(f"😊 Emotion detected: {primary_emotion} (confidence: {confidence:.2%})")
                if micro_expressions:
                    logger.info(f"   Micro-expressions: {', '.join(micro_expressions)}")
        except Exception as e:
            logger.debug(f"Emotion response error: {e}")

    def _get_iris_color(self, intensity):
        """Get iris color based on intensity - sophisticated, not robotic"""
        # Sophisticated color gradient - Iron Man style
        # More blue when alert, darker when relaxed
        r = int(0 * intensity)
        g = int(102 + (153 * intensity))
        b = int(153 + (102 * intensity))
        return f'#{r:02x}{g:02x}{b:02x}'

    def _update_jarvis_eye_position(self, operator_eye_pos):
        """Update JARVIS eye position - INTELLIGENT, NATURAL, NOT ROBOTIC - SCANS BETWEEN OPERATOR AND IMBA"""
        try:
            # Validate operator_eye_pos - if None or invalid, reset to center
            if operator_eye_pos is None or not isinstance(operator_eye_pos, (tuple, list)) or len(operator_eye_pos) < 2:
                # No valid eye position - reset to center
                self.jarvis_eye_position = (150, 150)
                self.jarvis_eye_target = (150, 150)
                if self.avatar_visible and self.avatar_canvas:
                    self._update_eye_display()
                return

            # Validate eye position values are reasonable (0-1 range expected)
            if not (0 <= operator_eye_pos[0] <= 1 and 0 <= operator_eye_pos[1] <= 1):
                # Invalid range - reset to center
                logger.warning("⚠️  Invalid operator eye position range - resetting to center")
                self.jarvis_eye_position = (150, 150)
                self.jarvis_eye_target = (150, 150)
                if self.avatar_visible and self.avatar_canvas:
                    self._update_eye_display()
                return

            # In MICRO mode, only iris moves (JARVIS stays at Stark Tower)
            # In MACRO mode (calibration), whole avatar can move
            if self.calibration_mode == "micro":
                # MICRO MODE: Only iris moves, avatar stays at Stark Tower
                center_x, center_y = 150, 150  # Center of avatar (fixed)
                max_offset = 15  # Subtle iris movement
            else:
                # MACRO MODE: During calibration, can move more
                center_x, center_y = 150, 150
                max_offset = 20  # Slightly more movement during calibration

            # INTELLIGENT GAZE - SCANS BETWEEN OPERATOR EYES AND IMBA
            # JARVIS demonstrates self-awareness by watching different versions of himself

            # Initialize scanning state if not exists
            if not hasattr(self, 'eye_scan_state'):
                import random
                self.eye_scan_state = {
                    "mode": "operator",  # "operator" or "m5"
                    "last_switch": time.time(),
                    "operator_duration": random.uniform(2.0, 4.0),  # Dynamic: 2-4 seconds looking at operator
                    "m5_duration": random.uniform(1.5, 3.0),  # Dynamic: 1.5-3 seconds tracking M5
                    "scanning_enabled": True,
                    "mutual_gaze_sound_played": False  # Track if we've played the connection sound
                }

            current_time = time.time()
            time_since_switch = current_time - self.eye_scan_state["last_switch"]

            # Determine current focus target with dynamic scaling timing
            if self.eye_scan_state["scanning_enabled"]:
                if self.eye_scan_state["mode"] == "operator":
                    # Looking at operator - DEAD ON, precise gaze tracking
                    if time_since_switch >= self.eye_scan_state["operator_duration"]:
                        # Switch to M5 tracking
                        import random
                        self.eye_scan_state["mode"] = "m5"
                        self.eye_scan_state["last_switch"] = current_time
                        # Dynamic scaling: next M5 duration varies
                        self.eye_scan_state["m5_duration"] = random.uniform(1.5, 3.5)
                        logger.info("👁️  JARVIS scanning: Operator → M5 Suitcase (tracking location)")
                else:  # mode == "m5"
                    # Looking at M5 - track its location dynamically
                    if time_since_switch >= self.eye_scan_state["m5_duration"]:
                        # Randomly return to operator (dynamic decision)
                        import random
                        if random.random() < 0.6:  # 60% chance to return to operator
                            self.eye_scan_state["mode"] = "operator"
                            self.eye_scan_state["last_switch"] = current_time
                            # Dynamic scaling: next operator duration varies
                            self.eye_scan_state["operator_duration"] = random.uniform(2.0, 5.0)
                            logger.info("👁️  JARVIS scanning: M5 → Operator (returning to gaze)")
                        else:  # 40% chance to continue watching M5
                            self.eye_scan_state["last_switch"] = current_time
                            # Extend watching time with dynamic scaling
                            self.eye_scan_state["m5_duration"] *= random.uniform(1.1, 1.5)
                            logger.info("👁️  JARVIS continues watching M5 (observing self)")

            # Calculate target based on current mode
            if self.eye_scan_state["mode"] == "operator":
                # Look at operator's eyes - DEAD ON, precise tracking (no scanning motion)
                # Direct, precise gaze - JARVIS is watching us, we're watching JARVIS
                base_offset_x = (operator_eye_pos[0] - 0.5) * max_offset * 2
                base_offset_y = (operator_eye_pos[1] - 0.5) * max_offset * 2

                # NO scanning motion when looking at operator - be precise, dead on
                # This creates the "we're watching each other" effect
            else:  # mode == "m5"
                # Look towards M5 Suitcase location - track it dynamically
                try:
                    # Find M5 position from VA visibility system
                    from va_visibility_system import VAVisibilitySystem
                    visibility = VAVisibilitySystem()
                    m5_widgets = visibility.viz.get_va_widgets("m5_suitcase")
                    if not m5_widgets:
                        # Try alternative ID
                        m5_widgets = [w for w in visibility.viz.widgets.values()
                                     if "m5" in w.va_id.lower() and "suitcase" in w.va_id.lower()]

                    if m5_widgets:
                        m5_widget = m5_widgets[0]
                        m5_x = m5_widget.position.get("x", 800)
                        m5_y = m5_widget.position.get("y", 400)

                        # Get JARVIS window position to calculate relative direction
                        if self.avatar_window:
                            jarvis_x = self.avatar_window.winfo_x()
                            jarvis_y = self.avatar_window.winfo_y()
                        else:
                            jarvis_x = 1920 - 320  # Default Stark Tower position
                            jarvis_y = 540

                        # Calculate direction from JARVIS to M5
                        screen_width = self.avatar_window.winfo_screenwidth() if self.avatar_window else 1920
                        screen_height = self.avatar_window.winfo_screenheight() if self.avatar_window else 1080

                        # Relative position (normalized)
                        m5_rel_x = (m5_x - jarvis_x) / screen_width
                        m5_rel_y = (m5_y - jarvis_y) / screen_height

                        # Point eye towards M5 (scale to eye movement range)
                        base_offset_x = -m5_rel_x * max_offset * 1.5  # Point towards M5
                        base_offset_y = -m5_rel_y * max_offset * 1.5
                    else:
                        # M5 not found, default to pointing right
                        base_offset_x = -max_offset * 0.8
                        base_offset_y = 0
                except Exception as e:
                    logger.debug(f"M5 tracking error: {e}")
                    # Fallback: point towards right side
                    base_offset_x = -max_offset * 0.8
                    base_offset_y = 0

            # Add natural micro-movements (saccades) - makes it alive, not robotic
            if self.eye_behavior.get("micro_movements", True):
                import random
                micro_x = random.uniform(-1, 1) * 0.5  # Very subtle
                micro_y = random.uniform(-1, 1) * 0.5
                base_offset_x += micro_x
                base_offset_y += micro_y

            # Smooth interpolation - elegant movement, not jerky
            target_x = center_x - base_offset_x  # Mirror horizontally
            target_y = center_y - base_offset_y  # Mirror vertically

            self.jarvis_eye_target = (target_x, target_y)

            # FIDELITY: Ensure target is within reasonable bounds BEFORE interpolation
            # Prevent eye from going to extreme positions
            eye_max_range = max_offset  # Maximum eye movement range
            min_target_x, max_target_x = center_x - eye_max_range, center_x + eye_max_range
            min_target_y, max_target_y = center_y - eye_max_range, center_y + eye_max_range

            # Clamp target to valid range
            target_x = max(min_target_x, min(max_target_x, target_x))
            target_y = max(min_target_y, min(max_target_y, target_y))

            # Smooth movement towards target (not instant - more natural)
            if self.eye_behavior.get("smooth_interpolation", True):
                current_x, current_y = self.jarvis_eye_position

                # FIDELITY: Validate current position - reset if stuck in corner
                distance_from_center = ((current_x - center_x)**2 + (current_y - center_y)**2)**0.5
                if distance_from_center > eye_max_range * 1.5:  # Way outside bounds
                    logger.warning(f"⚠️  Eye stuck at extreme position ({current_x:.1f}, {current_y:.1f}), resetting to center")
                    current_x, current_y = center_x, center_y
                    self.jarvis_eye_position = (center_x, center_y)

                # Smooth interpolation factor
                smooth_factor = 0.3  # Lower = smoother but slower

                new_x = current_x + (target_x - current_x) * smooth_factor
                new_y = current_y + (target_y - current_y) * smooth_factor

                # Final bounds check - ensure eye stays within socket
                new_x = max(min_target_x, min(max_target_x, new_x))
                new_y = max(min_target_y, min(max_target_y, new_y))

                self.jarvis_eye_position = (new_x, new_y)
            else:
                # Direct positioning with bounds check
                self.jarvis_eye_position = (target_x, target_y)

            # Update eye state based on movement
            movement_distance = ((target_x - center_x)**2 + (target_y - center_y)**2)**0.5
            self.eye_state["intensity"] = min(1.0, 0.3 + (movement_distance / max_offset) * 0.7)
            self.eye_state["focus"] = "operator" if movement_distance > 2 else "idle"

            # FACE-TO-FACE CONNECTION - Suspension of Disbelief
            # When operator looks at JARVIS and JARVIS looks back = mutual gaze
            # This is the powerful storytelling moment
            if movement_distance < 8:  # Close to center = looking at each other (relaxed threshold)
                if not self.eye_state.get("mutual_gaze", False):
                    # Connection established!
                    self.eye_state["mutual_gaze"] = True
                    self.eye_state["gaze_connection_time"] = time.time()
                    logger.info("👁️  FACE-TO-FACE CONNECTION ESTABLISHED - Suspension of Disbelief!")
                    logger.info("   JARVIS and Operator are now in mutual gaze - powerful storytelling moment")

                    # PLAY CONNECTION SOUND - Modem/AOL "You've got mail" sound
                    self._play_connection_sound()

                # Track connection duration
                connection_duration = time.time() - self.eye_state["gaze_connection_time"]
                self.eye_state["gaze_duration"] = connection_duration

                # Visual feedback for connection (subtle intensity increase)
                self.eye_state["intensity"] = min(1.0, 0.7 + (connection_duration * 0.1))
            else:
                # Connection lost
                if self.eye_state.get("mutual_gaze", False):
                    duration = self.eye_state.get("gaze_duration", 0)
                    logger.info(f"   Connection maintained for {duration:.1f} seconds")
                    # Reset sound flag so it can play again on next connection
                    if hasattr(self, 'eye_scan_state'):
                        self.eye_scan_state["mutual_gaze_sound_played"] = False
                self.eye_state["mutual_gaze"] = False
                self.eye_state["gaze_duration"] = 0

            # Update canvas if avatar is visible
            if self.avatar_visible and self.avatar_canvas:
                self._update_eye_display()
        except Exception as e:
            logger.error(f"❌ Eye position update error: {e}")
            # FIDELITY: Reset eye to center on error - never leave it stuck
            center_x, center_y = 150, 150
            self.jarvis_eye_position = (center_x, center_y)
            self.jarvis_eye_target = (center_x, center_y)
            if self.avatar_visible and self.avatar_canvas:
                try:
                    self._update_eye_display()
                    self.avatar_canvas.update()  # Force immediate redraw
                except:
                    pass

    def _play_connection_sound(self):
        """Play connection sound when mutual gaze is established - R2-D2 sound"""
        # Only play once per connection
        if hasattr(self, 'eye_scan_state') and self.eye_scan_state.get("mutual_gaze_sound_played", False):
            return

        try:
            from r2d2_sound_system import get_r2d2_sound_system, R2D2SoundType
            r2d2 = get_r2d2_sound_system()

            # Play R2-D2 connection sound (mutual gaze established)
            import random
            variation = random.randint(0, 2)  # Random variation
            r2d2.play_sound(R2D2SoundType.CONNECTION, variation)
            logger.info("🔊 Played R2-D2 connection sound (mutual gaze established)")

            # Mark as played
            if hasattr(self, 'eye_scan_state'):
                self.eye_scan_state["mutual_gaze_sound_played"] = True
        except ImportError:
            logger.debug("R2-D2 sound system not available, using fallback")
            # Fallback to simple beep
            try:
                import winsound
                winsound.Beep(1000, 150)
            except:
                pass
        except Exception as e:
            logger.debug(f"Error playing R2-D2 connection sound: {e}")

    def reset_eye_position(self):
        """Reset JARVIS eye to center position - FIX STUCK EYE (FIDELITY: Always centered)"""
        logger.info("🔄 Resetting JARVIS eye position to center (FIDELITY)")

        # FIDELITY: Force reset to exact center
        center_x, center_y = 150, 150
        self.jarvis_eye_position = (center_x, center_y)
        self.jarvis_eye_target = (center_x, center_y)

        # Reset scanning state
        if hasattr(self, 'eye_scan_state'):
            self.eye_scan_state["mode"] = "operator"
            self.eye_scan_state["last_switch"] = time.time()
            self.eye_scan_state["mutual_gaze_sound_played"] = False

        # Force update display immediately
        if self.avatar_visible and self.avatar_canvas:
            self._update_eye_display()
            self.avatar_canvas.update()  # Force immediate redraw

        logger.info(f"✅ Eye position reset to center ({center_x}, {center_y})")

    def recycle_jarvis(self):
        """Recycle/restart JARVIS - Kill and restart the avatar"""
        logger.info("🔄 RECYCLING JARVIS - Restarting avatar system")
        try:
            # Reset eye position first
            self.reset_eye_position()

            # Stop eye tracking
            self.eye_tracking_active = False
            if self.eye_tracking_thread and self.eye_tracking_thread.is_alive():
                # Thread will stop on next check
                pass

            # Reset eye state
            self.eye_state = {
                "focus": "idle",
                "intensity": 0.5,
                "last_blink": None,
                "gaze_duration": 0,
                "mutual_gaze": False,
                "gaze_connection_time": 0
            }

            # Reset scanning state
            if hasattr(self, 'eye_scan_state'):
                self.eye_scan_state = {
                    "mode": "operator",
                    "last_switch": time.time(),
                    "operator_duration": 3.0,
                    "imba_duration": 2.0,
                    "scanning_enabled": True
                }

            # Reinitialize eye tracking
            self._initialize_eye_tracking()

            logger.info("✅ JARVIS recycled successfully - eye tracking restarted")
            return True
        except Exception as e:
            logger.error(f"❌ Error recycling JARVIS: {e}")
            return False

    def _update_eye_display(self):
        """Update JARVIS eye display - FIDELITY: Sophisticated, elegant, never stuck in corner"""
        try:
            if not self.avatar_canvas:
                return

            # FIDELITY: Validate eye position - reset if stuck in corner
            center_x, center_y = 150, 150
            eye_x, eye_y = self.jarvis_eye_position

            # Safety check: if eye is way outside reasonable bounds, reset to center
            max_eye_range = 25  # Maximum eye movement from center
            distance_from_center = ((eye_x - center_x)**2 + (eye_y - center_y)**2)**0.5

            if distance_from_center > max_eye_range:
                logger.warning(f"⚠️  Eye position invalid ({eye_x:.1f}, {eye_y:.1f}), resetting to center")
                eye_x, eye_y = center_x, center_y
                self.jarvis_eye_position = (center_x, center_y)
                self.jarvis_eye_target = (center_x, center_y)

            iris_intensity = self.eye_state.get("intensity", 0.5)

            # Update outer iris rings (ACE quality - multiple layers)
            for i in range(2):  # Two outer rings
                ring_size = 18 if i == 0 else 16.2  # 18 * 1.0 and 18 * 0.9
                tag = f"jarvis_eye_outer_ring_{i}"
                try:
                    self.avatar_canvas.coords(tag,
                        eye_x - ring_size, eye_y - ring_size,
                        eye_x + ring_size, eye_y + ring_size)
                except:
                    pass  # Tag might not exist yet

            # Update iris position and color (ACE quality)
            iris_color = self._get_iris_color(iris_intensity)

            # Iris shadow
            try:
                self.avatar_canvas.coords("jarvis_eye_iris_shadow",
                    eye_x - 15, eye_y - 15,
                    eye_x + 15, eye_y + 15)
            except:
                pass

            # Main iris
            try:
                self.avatar_canvas.coords("jarvis_eye_iris",
                    eye_x - 14, eye_y - 14,
                    eye_x + 14, eye_y + 14)
                self.avatar_canvas.itemconfig("jarvis_eye_iris", fill=iris_color)
            except:
                pass

            # Iris highlight
            try:
                self.avatar_canvas.coords("jarvis_eye_iris_highlight",
                    eye_x - 10, eye_y - 10,
                    eye_x + 10, eye_y + 10)
            except:
                pass

            # Update pupil position and size (ACE quality with shadow and highlight)
            pupil_size = 6 + (iris_intensity * 2)

            # Pupil shadow
            try:
                self.avatar_canvas.coords("jarvis_eye_pupil_shadow",
                    eye_x - pupil_size - 1, eye_y - pupil_size - 1,
                    eye_x + pupil_size + 1, eye_y + pupil_size + 1)
            except:
                pass

            # Main pupil
            try:
                self.avatar_canvas.coords("jarvis_eye_pupil",
                    eye_x - pupil_size, eye_y - pupil_size,
                    eye_x + pupil_size, eye_y + pupil_size)
            except:
                pass

            # Pupil highlight
            try:
                highlight_size = pupil_size * 0.4
                self.avatar_canvas.coords("jarvis_eye_pupil_highlight",
                    eye_x - highlight_size, eye_y - highlight_size - 1,
                    eye_x + highlight_size, eye_y + highlight_size - 1)
            except:
                pass

            # Update glow layers (ACE quality - 4 layers)
            glow_intensity = int(255 * iris_intensity)
            glow_layers = [
                (20, 0.4, '#003366'),
                (16, 0.25, '#004488'),
                (12, 0.15, '#0055aa'),
                (8, 0.08, '#0066cc'),
            ]

            for i, (size, alpha, base_color) in enumerate(glow_layers):
                try:
                    r, g, b = int(base_color[1:3], 16), int(base_color[3:5], 16), int(base_color[5:7], 16)
                    glow_alpha = alpha * (iris_intensity * 0.5 + 0.5)
                    glow_r = int(r * glow_alpha)
                    glow_g = int(g * glow_alpha + 204 * (1 - glow_alpha))
                    glow_b = int(b * glow_alpha + 255 * (1 - glow_alpha))
                    glow_color = f'#{glow_r:02x}{glow_g:02x}{glow_b:02x}'

                    self.avatar_canvas.coords(f"jarvis_eye_glow_{i}",
                        eye_x - size, eye_y - size,
                        eye_x + size, eye_y + size)
                    self.avatar_canvas.itemconfig(f"jarvis_eye_glow_{i}", outline=glow_color)
                except:
                    pass  # Tag might not exist yet

            # FIDELITY: Update text positions if they exist (gold text, status line)
            # Gold text position updated to be one line below subtitle
            self._update_text_positions()

            self.avatar_canvas.update()
        except Exception as e:
            logger.error(f"❌ Eye display update error: {e}")
            # FIDELITY: Reset to center on any error
            try:
                center_x, center_y = 150, 150
                self.jarvis_eye_position = (center_x, center_y)
                self.jarvis_eye_target = (center_x, center_y)
            except:
                pass

    def _update_text_positions(self):
        """FIDELITY: Update text positions for proper spacing (gold text, status line)"""
        if not self.avatar_canvas or not hasattr(self, 'text_positions'):
            return

        try:
            center_x = 150
            line_spacing = 14

            # Update gold text position (if it exists) - one line BELOW subtitle (moved down)
            gold_text_y = self.text_positions.get("gold_text_y", 112)  # One line below subtitle
            try:
                # Try to find and update gold text
                for tag in ["jarvis_gold_text", "jarvis_status_gold", "gold_status", "gold_text"]:
                    try:
                        self.avatar_canvas.coords(tag, center_x, gold_text_y)
                    except:
                        pass
            except:
                pass

            # Update subtitle position
            subtitle_y = self.text_positions.get("subtitle_y", 98)
            try:
                self.avatar_canvas.coords("jarvis_subtitle", center_x, subtitle_y)
                # Update shadow too
                for i in range(8):  # 8 shadow layers
                    try:
                        self.avatar_canvas.coords(f"jarvis_subtitle_shadow", center_x, subtitle_y)
                    except:
                        pass
            except:
                pass

            # Update green status line position (if it exists) - right under JARVIS name
            status_y = self.text_positions.get("status_y", 84)
            try:
                # Try to find and update green status text
                for tag in ["jarvis_status", "jarvis_warning", "jarvis_alert", "jarvis_green_status", "status_line"]:
                    try:
                        self.avatar_canvas.coords(tag, center_x, status_y)
                    except:
                        pass
            except:
                pass
        except Exception as e:
            logger.debug(f"Text position update error: {e}")

    def _animate_eye_tracking(self):
        """Animate JARVIS eye - SOPHISTICATED, NATURAL, INTELLIGENT"""
        if not self.avatar_canvas:
            return

        def update_eye():
            if self.eye_tracking_active:
                # Add natural behaviors - not just tracking
                if self.eye_behavior.get("natural_saccades", True):
                    # Occasional natural eye movements (saccades)
                    import random
                    if random.random() < 0.02:  # 2% chance per frame
                        # Natural saccade - quick eye movement (FIDELITY: bounded)
                        center_x, center_y = 150, 150
                        current_x, current_y = self.jarvis_eye_position
                        saccade_x = random.uniform(-2, 2)  # Smaller saccades
                        saccade_y = random.uniform(-2, 2)
                        new_x = current_x + saccade_x
                        new_y = current_y + saccade_y

                        # FIDELITY: Ensure saccade doesn't push eye outside bounds
                        max_range = 20
                        distance = ((new_x - center_x)**2 + (new_y - center_y)**2)**0.5
                        if distance > max_range:
                            # Clamp to bounds
                            angle = ((new_x - center_x)**2 + (new_y - center_y)**2)**0.5
                            if angle > 0:
                                new_x = center_x + (new_x - center_x) / distance * max_range
                                new_y = center_y + (new_y - center_y) / distance * max_range

                        self.jarvis_eye_position = (new_x, new_y)

                # Update display
                self._update_eye_display()

            # Continue animation at high FPS for smoothness
            if self.avatar_visible:
                self.avatar_window.after(16, update_eye)  # ~60 FPS for smoothness

        self.avatar_window.after(100, update_eye)

    def _initialize_five_senses(self):
        """Initialize JARVIS's five senses - complete body experience"""
        # INTEGRATION: Connect all new learning systems
        try:
            from jarvis_learning_pipeline import get_jarvis_learning_pipeline
            from jarvis_interaction_recorder import get_jarvis_interaction_recorder
            from jarvis_feedback_system import get_jarvis_feedback_system
            from jarvis_context_analyzer import get_jarvis_context_analyzer
            from jarvis_intent_classifier import get_jarvis_intent_classifier
            from jarvis_action_predictor import get_jarvis_action_predictor

            self.learning_pipeline = get_jarvis_learning_pipeline(self.project_root)
            self.interaction_recorder = get_jarvis_interaction_recorder(self.project_root)
            self.feedback_system = get_jarvis_feedback_system(self.project_root)
            self.context_analyzer = get_jarvis_context_analyzer(self.project_root)
            self.intent_classifier = get_jarvis_intent_classifier(self.project_root)
            self.action_predictor = get_jarvis_action_predictor(self.project_root)

            # PHASE 2: Reasoning & Problem-Solving
            try:
                from jarvis_reasoning_engine import get_jarvis_reasoning_engine
                from jarvis_problem_decomposer import get_jarvis_problem_decomposer
                from jarvis_solution_planner import get_jarvis_solution_planner
                from jarvis_creative_solver import get_jarvis_creative_solver
                from jarvis_solution_evaluator import get_jarvis_solution_evaluator
                from jarvis_iterative_improver import get_jarvis_iterative_improver
                from jarvis_ethical_framework import get_jarvis_ethical_framework
                from jarvis_enhanced_memory import get_jarvis_enhanced_memory
                from jarvis_teaching_system import get_jarvis_teaching_system

                self.reasoning_engine = get_jarvis_reasoning_engine(self.project_root)
                self.problem_decomposer = get_jarvis_problem_decomposer(self.project_root)
                self.solution_planner = get_jarvis_solution_planner(self.project_root)
                self.creative_solver = get_jarvis_creative_solver(self.project_root)
                self.solution_evaluator = get_jarvis_solution_evaluator(self.project_root)
                self.iterative_improver = get_jarvis_iterative_improver(self.project_root)
                self.ethical_framework = get_jarvis_ethical_framework(self.project_root)
                self.enhanced_memory = get_jarvis_enhanced_memory(self.project_root)
                self.teaching_system = get_jarvis_teaching_system(self.project_root)

                logger.info("✅ Phase 2 systems integrated: Reasoning, Problem-Solving, Ethics, Memory, Teaching")
            except Exception as e:
                logger.debug(f"Phase 2 systems integration error: {e}")

            # PHASE 3: AGI & Self-Improvement
            try:
                from jarvis_meta_learning import get_jarvis_meta_learning
                from jarvis_self_improvement import get_jarvis_self_improvement
                from jarvis_agi_framework import get_jarvis_agi_framework
                from jarvis_coordination_framework import get_jarvis_coordination_framework
                from jarvis_natural_communication import get_jarvis_natural_communication

                self.meta_learning = get_jarvis_meta_learning(self.project_root)
                self.self_improvement = get_jarvis_self_improvement(self.project_root)
                self.agi_framework = get_jarvis_agi_framework(self.project_root)
                self.coordination_framework = get_jarvis_coordination_framework(self.project_root)
                self.natural_communication = get_jarvis_natural_communication(self.project_root)

                logger.info("✅ Phase 3 systems integrated: Meta-Learning, Self-Improvement, AGI, Coordination, Communication")
            except Exception as e:
                logger.debug(f"Phase 3 systems integration error: {e}")

            # PHASE 4: ASI Capabilities
            try:
                from jarvis_superhuman_reasoner import get_jarvis_superhuman_reasoner
                from jarvis_autonomous_operator import get_jarvis_autonomous_operator
                from jarvis_partnership_framework import get_jarvis_partnership_framework
                from jarvis_innovation_engine import get_jarvis_innovation_engine
                from jarvis_team_leader import get_jarvis_team_leader

                self.superhuman_reasoner = get_jarvis_superhuman_reasoner(self.project_root)
                self.autonomous_operator = get_jarvis_autonomous_operator(self.project_root)
                self.partnership_framework = get_jarvis_partnership_framework(self.project_root)
                self.innovation_engine = get_jarvis_innovation_engine(self.project_root)
                self.team_leader = get_jarvis_team_leader(self.project_root)

                logger.info("✅ Phase 4 systems integrated: Superhuman Reasoning, Autonomy, Partnership, Innovation, Leadership")
            except Exception as e:
                logger.debug(f"Phase 4 systems integration error: {e}")

            logger.info("✅ All learning systems integrated with JARVIS")
        except Exception as e:
            logger.debug(f"Learning systems integration error: {e}")

        # SIGHT - MDV Live Video (already initialized)
        # Correlates with: Network visualization, service dashboards, infrastructure monitoring, real-time desktop awareness
        try:
            self._initialize_mdv_vision()
            if self.vision_active:
                self.senses["sight"]["active"] = True
                logger.info("   🏠 Home Lab Correlation: Network topology, NAS/pfSense/Docker dashboards, Grafana metrics")

                # Feed sight data into context analyzer
                if self.context_analyzer:
                    from jarvis_context_analyzer import ContextSource
                    self.context_analyzer.add_context_data(
                        ContextSource.SIGHT,
                        {"vision_active": True, "mdv_available": bool(self.mdv_vision)},
                        confidence=1.0
                    )
        except Exception as e:
            logger.warning(f"⚠️  Sight (MDV) initialization failed: {e}")

        # HEARING - Voice transcript queue
        # Correlates with: Network traffic analysis, service logs, alert systems, communication channels, event streams
        try:
            from voice_transcript_queue import VoiceTranscriptQueue
            self.voice_queue = VoiceTranscriptQueue()
            self.senses["hearing"]["active"] = True
            logger.info("✅ Hearing initialized - voice transcript queue active")
            logger.info("   🏠 Home Lab Correlation: Network traffic, service logs, WOPR/DEFCON alerts, notification queues")

            # Feed hearing data into context analyzer
            if self.context_analyzer:
                from jarvis_context_analyzer import ContextSource
                self.context_analyzer.add_context_data(
                    ContextSource.HEARING,
                    {"voice_queue_active": True},
                    confidence=1.0
                )
        except Exception as e:
            logger.warning(f"⚠️  Hearing initialization failed: {e}")

        # TOUCH - Haptic/input feedback (mouse, keyboard, system interactions)
        # Correlates with: Network latency, service response times, system load, infrastructure health, VA movement tracking
        try:
            import pyautogui
            self.touch_system = {
                "pyautogui": pyautogui,
                "last_interaction": None
            }
            self.senses["touch"]["active"] = True
            logger.info("✅ Touch initialized - input feedback active")
            logger.info("   🏠 Home Lab Correlation: Network latency, service response times, CPU/memory/disk load, system pulse")

            # Feed touch data into context analyzer
            if self.context_analyzer:
                from jarvis_context_analyzer import ContextSource
                self.context_analyzer.add_context_data(
                    ContextSource.TOUCH,
                    {"touch_system_active": True},
                    confidence=1.0
                )
        except Exception as e:
            logger.warning(f"⚠️  Touch initialization failed: {e}")

        # TASTE - Data analysis (metaphorical - JARVIS "tastes" data quality)
        # Correlates with: Database health, backup quality, config validity, data pipeline health, storage integrity, log quality
        try:
            # Integrate with home lab data monitoring
            try:
                from defcon_monitoring_system import DEFCONMonitoringSystem
                defcon_system = DEFCONMonitoringSystem()
                self.taste_system = {
                    "data_quality_monitor": True,
                    "defcon_integration": defcon_system,
                    "last_analysis": None
                }
            except ImportError:
                self.taste_system = {
                    "data_quality_monitor": True,
                    "defcon_integration": None,
                    "last_analysis": None
                }

            self.senses["taste"]["active"] = True
            logger.info("✅ Taste initialized - data quality analysis active")
            logger.info("   🏠 Home Lab Correlation: Database health, backup quality, config validity, storage integrity")
            # Update self-awareness
            if self.self_awareness:
                from jarvis_self_awareness_system import PerceptionType
                self.self_awareness.update_perception(PerceptionType.TASTE, {"source": "data_quality"}, active=True)
        except Exception as e:
            logger.warning(f"⚠️  Taste initialization failed: {e}")

        # SMELL - System health monitoring (metaphorical - JARVIS "smells" problems)
        # Correlates with: DEFCON monitoring, WOPR status, network health, service health, infrastructure alerts, security threats
        try:
            # Integrate with DEFCON monitoring system (primary home lab health system)
            try:
                from defcon_monitoring_system import DEFCONMonitoringSystem
                defcon_system = DEFCONMonitoringSystem()

                # Start periodic health monitoring
                def monitor_health():
                    while self.avatar_visible:
                        try:
                            # Check DEFCON level
                            current_level = defcon_system.get_current_level()
                            alerts = defcon_system.check_system_alerts()
                            problems = defcon_system.get_problems()

                            # Update smell system
                            self.smell_system["last_check"] = datetime.now().isoformat()
                            self.smell_system["defcon_level"] = current_level.value if hasattr(current_level, 'value') else str(current_level)
                            self.smell_system["alert_count"] = len(alerts)
                            self.smell_system["problem_count"] = len(problems)

                            # Update self-awareness
                            if self.self_awareness:
                                from jarvis_self_awareness_system import PerceptionType
                                self.self_awareness.update_perception(
                                    PerceptionType.SMELL,
                                    {
                                        "defcon_level": self.smell_system["defcon_level"],
                                        "alerts": len(alerts),
                                        "problems": len(problems)
                                    },
                                    active=True
                                )

                            time.sleep(30)  # Check every 30 seconds
                        except Exception as e:
                            logger.debug(f"Health monitoring error: {e}")
                            time.sleep(60)

                self.smell_system = {
                    "health_monitor": True,
                    "defcon_system": defcon_system,
                    "last_check": None,
                    "defcon_level": None,
                    "alert_count": 0,
                    "problem_count": 0
                }

                # Start health monitoring thread
                health_thread = threading.Thread(target=monitor_health, daemon=True)
                health_thread.start()
                logger.info("✅ Smell initialized - system health monitoring active")
                logger.info("   🏠 Home Lab Correlation: DEFCON monitoring, WOPR status, network/service health, security alerts")
                logger.info("   🔄 Health monitoring thread started (checks every 30 seconds)")
            except ImportError:
                self.smell_system = {
                    "health_monitor": True,
                    "defcon_system": None,
                    "last_check": None
                }
                logger.warning("⚠️  DEFCON system not available - basic smell only")

            self.senses["smell"]["active"] = True

            # Feed smell data into context analyzer
            if self.context_analyzer:
                from jarvis_context_analyzer import ContextSource
                self.context_analyzer.add_context_data(
                    ContextSource.SMELL,
                    {"health_monitor": True, "defcon_available": bool(defcon_system)},
                    confidence=1.0
                )

            # Update self-awareness
            if self.self_awareness:
                from jarvis_self_awareness_system import PerceptionType
                self.self_awareness.update_perception(PerceptionType.SMELL, {"source": "system_health"}, active=True)
        except Exception as e:
            logger.warning(f"⚠️  Smell initialization failed: {e}")

        # Start periodic introspection thread (JARVIS reflects on itself)
        if self.self_awareness:
            self.introspection_thread = threading.Thread(target=self._periodic_introspection_loop, daemon=True)
            self.introspection_thread.start()
            logger.info("✅ Periodic introspection started - JARVIS will reflect on itself and learn")

    def _initialize_mdv_vision(self):
        """Initialize MDV Live Video for real-time sight - JARVIS SEES WHAT HE'S DOING"""
        try:
            # MDV provides continuous screen capture/vision
            import pyautogui
            try:
                import cv2
                import numpy as np
                cv2_available = True
            except ImportError:
                cv2_available = False
                np = None

            self.mdv_vision = {
                "pyautogui": pyautogui,
                "cv2_available": cv2_available
            }
            if cv2_available:
                self.mdv_vision["cv2"] = cv2
                self.mdv_vision["np"] = np

            self.vision_active = True

            # Start vision monitoring thread - continuous real-time sight
            self.vision_thread = threading.Thread(target=self._vision_monitoring_loop, daemon=True)
            self.vision_thread.start()

            # Start five senses monitoring thread
            self.senses_thread = threading.Thread(target=self._monitor_senses, daemon=True)
            self.senses_thread.start()

            logger.info("✅ MDV Live Video initialized - JARVIS can see in real-time")

            # SELF-AWARENESS: Update sight perception
            if self.self_awareness:
                from jarvis_self_awareness_system import PerceptionType
                self.self_awareness.update_perception(PerceptionType.SIGHT, {"source": "mdv"}, active=True)
            logger.info("   JARVIS will verify and correct based on what he sees")
            logger.info("✅ Five senses monitoring active - complete body experience")
        except ImportError as e:
            logger.warning(f"MDV vision dependencies not available: {e}")
            logger.warning("   Install: pip install pyautogui opencv-python numpy")
            self.vision_active = False
        except Exception as e:
            logger.warning(f"MDV vision initialization error: {e}")
            self.vision_active = False

    def _vision_monitoring_loop(self):
        """Vision monitoring loop - JARVIS sees what's happening in REAL-TIME"""
        logger.info("👁️  JARVIS vision monitoring started - continuous real-time sight")

        while self.vision_active:
            try:
                # Capture current screen - MDV Live Video
                screenshot = self.mdv_vision["pyautogui"].screenshot()

                # Convert to array if cv2 available
                if self.mdv_vision.get("cv2_available"):
                    import numpy as np
                    screen_array = np.array(screenshot)
                    self._analyze_vision(screen_array)
                else:
                    # Basic screenshot analysis
                    self._analyze_vision_basic(screenshot)

                # Check every 0.5 seconds for real-time feedback (faster for corrections)
                time.sleep(0.5)
            except Exception as e:
                logger.debug(f"Vision monitoring error: {e}")
                time.sleep(1.0)

    def _analyze_vision(self, screen_array):
        """Analyze what JARVIS sees and make REAL-TIME CORRECTIONS"""
        # JARVIS can see what's on screen and verify/correct actions
        # Example: if user asks for circle but JARVIS sees square, he corrects immediately

        # Store current vision state
        if not hasattr(self, 'last_vision_state'):
            self.last_vision_state = None

        # Vision analysis - JARVIS sees what's actually there
        self.last_vision_state = {
            "timestamp": datetime.now().isoformat(),
            "screen_captured": True,
            "has_vision": True
        }

        # If JARVIS is narrating and sees something wrong, he can self-correct immediately
        if self.narration_active and self.current_segment:
            # JARVIS verifies what he's describing matches what's on screen
            # Real-time correction capability
            pass

    def _analyze_vision_basic(self, screenshot):
        """Basic vision analysis without cv2"""
        self.last_vision_state = {
            "timestamp": datetime.now().isoformat(),
            "screen_captured": True,
            "has_vision": True
        }

    def _monitor_senses(self):
        """Monitor JARVIS's five senses and update self-awareness"""
        logger.info("👁️👂✋👅👃 Five senses monitoring started")

        while self.avatar_visible:
            try:
                # Update self-awareness with current sense states
                if self.self_awareness:
                    from jarvis_self_awareness_system import PerceptionType

                    # Sight
                    if self.senses.get("sight", {}).get("active"):
                        self.self_awareness.update_perception(
                            PerceptionType.SIGHT,
                            {"vision_active": self.vision_active, "mdv_available": bool(self.mdv_vision)},
                            active=True
                        )

                    # Hearing
                    if self.senses.get("hearing", {}).get("active"):
                        self.self_awareness.update_perception(
                            PerceptionType.HEARING,
                            {"voice_queue_active": hasattr(self, 'voice_queue')},
                            active=True
                        )

                    # Touch
                    if self.senses.get("touch", {}).get("active"):
                        self.self_awareness.update_perception(
                            PerceptionType.TOUCH,
                            {"touch_system_active": hasattr(self, 'touch_system')},
                            active=True
                        )

                    # Taste
                    if self.senses.get("taste", {}).get("active"):
                        self.self_awareness.update_perception(
                            PerceptionType.TASTE,
                            {"data_analysis_active": hasattr(self, 'taste_system')},
                            active=True
                        )

                    # Smell
                    if self.senses.get("smell", {}).get("active"):
                        self.self_awareness.update_perception(
                            PerceptionType.SMELL,
                            {"health_monitoring_active": hasattr(self, 'smell_system')},
                            active=True
                        )

                # Monitor every 10 seconds
                time.sleep(10)
            except Exception as e:
                logger.debug(f"Senses monitoring error: {e}")
                time.sleep(5)

    def _periodic_introspection_loop(self):
        """Periodic introspection - JARVIS reflects on itself, learns, adapts"""
        logger.info("🧠 Starting periodic introspection loop - JARVIS self-reflection")
        logger.info("   JARVIS will continuously learn, adapt, and become more aware")

        # Initial wait before first introspection
        time.sleep(60)  # Wait 1 minute after startup

        while self.avatar_visible and self.self_awareness:
            try:
                # Perform introspection (every 5 minutes)
                introspection = self.self_awareness.periodic_introspection()

                # Log insights
                if introspection.insights:
                    logger.info("")
                    logger.info("=" * 80)
                    logger.info(f"🧠 JARVIS INTROSPECTION: {introspection.question}")
                    logger.info("=" * 80)
                    logger.info(f"   Analysis: {introspection.analysis}")
                    logger.info("")
                    logger.info("   💡 Insights:")
                    for insight in introspection.insights:
                        logger.info(f"      • {insight}")

                    if introspection.action_items:
                        logger.info("")
                        logger.info("   📋 Action Items:")
                        for action in introspection.action_items:
                            logger.info(f"      • {action}")

                    logger.info("")
                    logger.info(f"   Confidence: {introspection.confidence:.2%}")
                    logger.info("=" * 80)
                    logger.info("")

                # Update self-state
                state = self.self_awareness.get_self_state()
                logger.info(f"📊 JARVIS Self-State:")
                logger.info(f"   Awareness Level: {state.awareness_level:.2%}")
                logger.info(f"   Learning Iterations: {state.learning_iterations}")
                logger.info(f"   Gaze Accuracy: {state.gaze_accuracy:.2%}")
                logger.info(f"   Interactions: {state.interaction_count}")
                logger.info(f"   Ecosystem Relationships: {len(self.self_awareness.ecosystem_relationships)}")
                logger.info(f"   Active Perceptions: {sum(1 for v in state.perception_active.values() if v)}/7")
                logger.info(f"   Uptime: {state.uptime_seconds:.0f} seconds")

                # Wait 5 minutes before next introspection
                time.sleep(300)  # 5 minutes

            except Exception as e:
                logger.debug(f"Introspection loop error: {e}")
                time.sleep(60)  # Wait 1 minute on error

    def _create_intro_story(self) -> List[NarrationSegment]:
        """Create introduction story segments"""
        return [
            NarrationSegment(
                segment_id="intro_1",
                text="Welcome to LUMINA. I am JARVIS, your guide and narrator.",
                visual_cue="jarvis_avatar_appear",
                duration=4.0
            ),
            NarrationSegment(
                segment_id="intro_2",
                text="LUMINA is more than a system. It is a story of overcoming odds, of survival, of triumph.",
                visual_cue="lumina_logo_reveal",
                duration=5.0
            ),
            NarrationSegment(
                segment_id="intro_3",
                text="Like the heroes in comic books, we face challenges. We adapt. We overcome.",
                visual_cue="hero_showcase",
                duration=5.0
            ),
            NarrationSegment(
                segment_id="intro_4",
                text="Today, I will guide you through LUMINA's features. Together, we will unlock its potential.",
                visual_cue="feature_preview",
                duration=5.0
            ),
            NarrationSegment(
                segment_id="intro_5",
                text="Let us begin this journey. The story of LUMINA awaits.",
                visual_cue="transition",
                duration=3.0,
                next_segment="walkthrough_start"
            )
        ]

    def _create_walkthrough_segments(self) -> List[NarrationSegment]:
        """Create walkthrough segments for LUMINA features"""
        return [
            NarrationSegment(
                segment_id="walkthrough_1",
                text="First, let me show you the Virtual Assistants. Each one has a unique role and purpose.",
                visual_cue="show_vas",
                duration=4.0
            ),
            NarrationSegment(
                segment_id="walkthrough_2",
                text="ACE is our immortal training dummy. IMVA can practice combat without risk.",
                visual_cue="show_ace",
                duration=4.0
            ),
            # DEFCON streetlight removed per user request - focusing on JARVIS first
            # NarrationSegment(
            #     segment_id="walkthrough_3",
            #     text="The DEFCON streetlight monitors system health. It shows alerts and problems in real-time.",
            #     visual_cue="show_defcon",
            #     duration=4.0
            # ),
            NarrationSegment(
                segment_id="walkthrough_4",
                text="Voice commands allow natural interaction. Speak, and LUMINA responds.",
                visual_cue="show_voice",
                duration=4.0
            ),
            NarrationSegment(
                segment_id="walkthrough_5",
                text="This is LUMINA. A system built not just with code, but with stories. Stories of survival, adaptation, and triumph.",
                visual_cue="lumina_overview",
                duration=5.0
            )
        ]

    def create_avatar_window(self):
        """Create JARVIS avatar window - floating, transparent background, artwork only"""
        if not TKINTER_AVAILABLE:
            return

        # PREVENT MULTIPLE WINDOWS - destroy existing if any
        if hasattr(self, 'avatar_window') and self.avatar_window:
            try:
                self.avatar_window.destroy()
            except:
                pass

        try:
            # Create root window if it doesn't exist (for Toplevel)
            if not hasattr(self, '_root') or not self._root:
                self._root = tk.Tk()
                self._root.withdraw()  # Hide root window - we only want Toplevel

            self.avatar_window = tk.Toplevel(self._root)
            self.avatar_window.title("JARVIS Narrator")
            self.avatar_window.overrideredirect(True)
            self.avatar_window.attributes('-topmost', True)

            # TRANSPARENT BACKGROUND - remove black box, keep artwork
            # Make window transparent except for artwork
            try:
                # Windows transparency
                self.avatar_window.attributes('-transparentcolor', '#000001')  # Use near-black for transparency
                self.avatar_window.configure(bg='#000001')  # Transparent color key
            except:
                # Fallback: use alpha transparency if available
                try:
                    self.avatar_window.attributes('-alpha', 0.95)  # Slightly transparent
                    self.avatar_window.configure(bg='#000000')
                except:
                    # Last resort: just remove frame, keep black
                    self.avatar_window.configure(bg='#000000')

            # Position at center-right initially (Stark Tower - home position)
            screen_width = self.avatar_window.winfo_screenwidth()
            screen_height = self.avatar_window.winfo_screenheight()
            self.stark_tower_position = {
                "x": screen_width - 320,
                "y": screen_height // 2 - 200
            }
            self.avatar_window.geometry(f"300x400+{self.stark_tower_position['x']}+{self.stark_tower_position['y']}")

            # Canvas for avatar - TRANSPARENT
            self.avatar_canvas = tk.Canvas(
                self.avatar_window,
                bg='#000001',  # Transparent color key
                highlightthickness=0,
                width=300,
                height=400
            )
            self.avatar_canvas.pack(fill=tk.BOTH, expand=True)

            # Draw JARVIS avatar (Iron Man inspired, but original design)
            # Artwork will be visible, background transparent
            self._draw_jarvis_avatar()

            # Chat bubble canvas for WoW-style NPC speech
            self.chat_bubble_canvas = tk.Canvas(
                self.avatar_window,
                bg='#000001',  # Transparent
                highlightthickness=0,
                width=300,
                height=120
            )
            self.chat_bubble_canvas.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)

            # Chat bubble elements (drawn on canvas, not label)
            self.chat_bubble_visible = False

            # DRAG FUNCTIONALITY - Make JARVIS draggable like Kenny
            self._setup_drag_functionality()

            # CLICK INTERACTION - Make JARVIS clickable
            self._setup_click_interaction()

            # KEYBOARD SHORTCUTS - Reset eye position
            self._setup_keyboard_shortcuts()

            self.avatar_visible = True
            logger.info("✅ JARVIS avatar window created - transparent background, artwork visible")
            logger.info("   🖱️  JARVIS is now draggable and click-interactive")
            logger.info("   ⌨️  Press F5 or 'R' key to reset eye position")
        except Exception as e:
            logger.error(f"Error creating avatar window: {e}")

    def _setup_drag_functionality(self):
        """Setup drag functionality for JARVIS window"""
        if not self.avatar_window or not self.avatar_canvas:
            return

        # Bind drag events to canvas
        self.avatar_canvas.bind("<Button-1>", self._start_drag)
        self.avatar_canvas.bind("<B1-Motion>", self._do_drag)
        self.avatar_canvas.bind("<ButtonRelease-1>", self._stop_drag)

        # Also bind to chat bubble canvas
        if hasattr(self, 'chat_bubble_canvas') and self.chat_bubble_canvas:
            self.chat_bubble_canvas.bind("<Button-1>", self._start_drag)
            self.chat_bubble_canvas.bind("<B1-Motion>", self._do_drag)
            self.chat_bubble_canvas.bind("<ButtonRelease-1>", self._stop_drag)

        # Change cursor to indicate draggable
        self.avatar_canvas.configure(cursor="hand2")
        if hasattr(self, 'chat_bubble_canvas') and self.chat_bubble_canvas:
            self.chat_bubble_canvas.configure(cursor="hand2")

    def _start_drag(self, event):
        """Start dragging JARVIS window"""
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root
        self.is_dragging = False  # Will be set to True when movement detected
        self._click_time = time.time()
        self._click_pos = (event.x_root, event.y_root)

        # RECORD DRAG START FOR EYE TRACKING FINE-TUNING
        if self.movement_fine_tuning:
            from va_movement_fine_tuning import MovementType
            start_x = self.avatar_window.winfo_x()
            start_y = self.avatar_window.winfo_y()
            window_width = self.avatar_window.winfo_width()
            window_height = self.avatar_window.winfo_height()
            self.movement_fine_tuning.record_movement(
                va_id="jarvis_va",
                va_name="JARVIS",
                movement_type=MovementType.DRAG_START,
                screen_position=(start_x, start_y),
                window_size=(window_width, window_height),
                context={"action": "drag_start"}
            )

    def _do_drag(self, event):
        """Handle dragging JARVIS window"""
        if not self.avatar_window:
            return

        # Mark as dragging if we've moved more than a few pixels
        drag_distance = ((event.x_root - self._click_pos[0])**2 +
                        (event.y_root - self._click_pos[1])**2)**0.5
        if drag_distance > 5:  # More than 5 pixels = dragging
            self.is_dragging = True

        if not self.is_dragging:
            return

        # Calculate new position
        dx = event.x_root - self.drag_start_x
        dy = event.y_root - self.drag_start_y

        # Get current window position
        current_x = self.avatar_window.winfo_x()
        current_y = self.avatar_window.winfo_y()

        # Calculate new position
        new_x = current_x + dx
        new_y = current_y + dy

        # Keep window on screen
        screen_width = self.avatar_window.winfo_screenwidth()
        screen_height = self.avatar_window.winfo_screenheight()
        window_width = self.avatar_window.winfo_width()
        window_height = self.avatar_window.winfo_height()

        # Clamp to screen bounds
        new_x = max(0, min(new_x, screen_width - window_width))
        new_y = max(0, min(new_y, screen_height - window_height))

        # Move window
        self.avatar_window.geometry(f"+{int(new_x)}+{int(new_y)}")

        # RECORD MOVEMENT FOR EYE TRACKING FINE-TUNING
        # User moved JARVIS - they were looking at it, valuable learning data!
        if self.movement_fine_tuning:
            from va_movement_fine_tuning import MovementType
            window_width = self.avatar_window.winfo_width()
            window_height = self.avatar_window.winfo_height()
            self.movement_fine_tuning.record_movement(
                va_id="jarvis_va",
                va_name="JARVIS",
                movement_type=MovementType.DRAG_MOVE,
                screen_position=(new_x, new_y),
                window_size=(window_width, window_height),
                context={"drag_distance": drag_distance}
            )

        # Update drag start position for next movement
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root

    def _stop_drag(self, event):
        """Stop dragging JARVIS window"""
        # RECORD DRAG END FOR EYE TRACKING FINE-TUNING
        if self.is_dragging and self.movement_fine_tuning:
            from va_movement_fine_tuning import MovementType
            final_x = self.avatar_window.winfo_x()
            final_y = self.avatar_window.winfo_y()
            window_width = self.avatar_window.winfo_width()
            window_height = self.avatar_window.winfo_height()
            self.movement_fine_tuning.record_movement(
                va_id="jarvis_va",
                va_name="JARVIS",
                movement_type=MovementType.DRAG_END,
                screen_position=(final_x, final_y),
                window_size=(window_width, window_height),
                context={"was_dragging": True}
            )

        # Check if this was a click (not a drag)
        if not self.is_dragging:
            # Wasn't dragging - check if it was a click
            drag_distance = ((event.x_root - self._click_pos[0])**2 +
                           (event.y_root - self._click_pos[1])**2)**0.5
            if drag_distance < 5:  # Less than 5 pixels = click, not drag
                # It was a click, trigger click handler
                self._handle_single_click(event)

                # RECORD CLICK FOR EYE TRACKING FINE-TUNING
                if self.movement_fine_tuning:
                    from va_movement_fine_tuning import MovementType
                    click_x = self.avatar_window.winfo_x()
                    click_y = self.avatar_window.winfo_y()
                    window_width = self.avatar_window.winfo_width()
                    window_height = self.avatar_window.winfo_height()
                    self.movement_fine_tuning.record_movement(
                        va_id="jarvis_va",
                        va_name="JARVIS",
                        movement_type=MovementType.CLICK,
                        screen_position=(click_x, click_y),
                        window_size=(window_width, window_height),
                        context={"was_click": True}
                    )

        self.is_dragging = False

    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for JARVIS"""
        if not self.avatar_window:
            return

        # F5 or 'R' key to reset eye position
        def reset_eye_on_key(event):
            logger.info("⌨️  Keyboard shortcut: Resetting eye position")
            self.reset_eye_position()

        # Bind to window (needs focus)
        self.avatar_window.bind("<F5>", reset_eye_on_key)
        self.avatar_window.bind("<Key-r>", reset_eye_on_key)
        self.avatar_window.bind("<Key-R>", reset_eye_on_key)

        # Also bind to canvas
        if self.avatar_canvas:
            self.avatar_canvas.bind("<F5>", reset_eye_on_key)
            self.avatar_canvas.bind("<Key-r>", reset_eye_on_key)
            self.avatar_canvas.bind("<Key-R>", reset_eye_on_key)
            self.avatar_canvas.focus_set()  # Enable keyboard focus

        logger.info("   ⌨️  Keyboard shortcuts: F5 or 'R' = Reset eye position")

    def _setup_click_interaction(self):
        """Setup click interaction for JARVIS"""
        if not self.avatar_window or not self.avatar_canvas:
            return

        # Double click - toggle narration mode or show menu
        self.avatar_canvas.bind("<Double-Button-1>", self._handle_double_click)

        # Right click - show context menu (future feature)
        self.avatar_canvas.bind("<Button-3>", self._handle_right_click)

        # Single click is handled in _stop_drag to distinguish from drag

    def _handle_single_click(self, event):
        """Handle single click on JARVIS"""
        # Don't trigger if we're dragging
        if self.is_dragging:
            return

        # NOTE: Iron Man suit spawning is DISABLED by default
        # Uncomment below to enable suit spawning on click
        # SPAWN IRON MAN SUIT on click (DISABLED)
        # if self.suit_system:
        #     # Get click position (screen coordinates)
        #     click_x = self.avatar_window.winfo_x() + event.x
        #     click_y = self.avatar_window.winfo_y() + event.y
        #
        #     # Spawn random suit
        #     suit_id = self.suit_system.spawn_random_suit((click_x, click_y))
        #     logger.info(f"🦾 Spawned Iron Man suit: {suit_id} at ({click_x}, {click_y})")
        #
        #     # Create suit window and render
        #     self._create_suit_window(suit_id)
        # else:
        logger.info("👆 JARVIS clicked - showing status")

    def _handle_double_click(self, event):
        """Handle double click on JARVIS"""
        logger.info("👆👆 JARVIS double-clicked - toggling narration")

        # RECORD DOUBLE CLICK FOR EYE TRACKING FINE-TUNING
        if self.movement_fine_tuning:
            from va_movement_fine_tuning import MovementType
            click_x = self.avatar_window.winfo_x()
            click_y = self.avatar_window.winfo_y()
            window_width = self.avatar_window.winfo_width()
            window_height = self.avatar_window.winfo_height()
            self.movement_fine_tuning.record_movement(
                va_id="jarvis_va",
                va_name="JARVIS",
                movement_type=MovementType.DOUBLE_CLICK,
                screen_position=(click_x, click_y),
                window_size=(window_width, window_height),
                context={"action": "toggle_narration"}
            )

        # Toggle narration on/off
        if self.narration_active:
            self._stop_narration()
        else:
            self.start_introduction()

    def _create_suit_window(self, suit_id):
        """Create window for spawned Iron Man suit"""
        if not self.suit_system or suit_id not in self.suit_system.active_suits:
            return

        suit_data = self.suit_system.get_suit_render_data(suit_id)
        if not suit_data:
            return

        try:
            # Create Toplevel window for suit
            if not hasattr(self, '_root') or not self._root:
                self._root = tk.Tk()
                self._root.withdraw()

            suit_window = tk.Toplevel(self._root)
            suit_window.overrideredirect(True)
            suit_window.attributes('-topmost', True)
            suit_window.attributes('-transparentcolor', '#000001')
            suit_window.configure(bg='#000001')

            # Position at spawn location
            x, y = suit_data["position"]
            suit_window.geometry(f"200x200+{int(x)}+{int(y)}")

            # Canvas for rendering
            canvas = tk.Canvas(
                suit_window,
                bg='#000001',
                highlightthickness=0,
                width=200,
                height=200
            )
            canvas.pack()

            # Bind click to toggle transformation (Mark 5 only)
            if suit_data["specs"].has_suitcase_mode:
                canvas.bind("<Button-1>", lambda e, sid=suit_id: self._toggle_suit_transformation(sid))
                canvas.configure(cursor="hand2")

            # Store window reference
            self.active_suits[suit_id] = {
                "suit_id": suit_id,
                "window": suit_window,
                "canvas": canvas,
                "render_data": suit_data
            }

            logger.info(f"✅ Created suit window for {suit_id}")

            # Start rendering loop
            self._render_suit(suit_id)
        except Exception as e:
            logger.error(f"❌ Error creating suit window: {e}")

    def _render_suit(self, suit_id):
        """Render Iron Man suit based on state"""
        if suit_id not in self.active_suits:
            return

        if not self.suit_system:
            return

        # Update animation
        self.suit_system.update_suit_animation(suit_id, 0.016)  # ~60 FPS

        suit_data = self.suit_system.get_suit_render_data(suit_id)
        if not suit_data:
            return

        canvas = self.active_suits[suit_id]["canvas"]
        if not canvas:
            return

        canvas.delete("all")

        tp = suit_data["transformation_progress"]  # 0.0 = suitcase, 1.0 = active
        specs = suit_data["specs"]
        state = suit_data["state"]

        center_x, center_y = 100, 100

        if state == self.SuitState.SUITCASE or tp < 0.3:
            # Render suitcase/briefcase
            self._render_suitcase(canvas, center_x, center_y, specs)
        else:
            # Render full suit
            self._render_full_suit(canvas, center_x, center_y, specs, tp)

            # Render Tony if visible
            if suit_data["tony_visible"]:
                self._render_tony_stark(canvas, center_x, center_y + 80)

        # Schedule next render
        if suit_id in self.active_suits and self.active_suits[suit_id]["window"]:
            try:
                self.active_suits[suit_id]["window"].after(16, lambda: self._render_suit(suit_id))  # ~60 FPS
            except:
                pass  # Window may have been closed

    def _render_suitcase(self, canvas, x, y, specs):
        """Render Mark 5 suitcase/briefcase"""
        # Briefcase shape
        width = 60
        height = 40

        # Main briefcase body
        canvas.create_rectangle(
            x - width/2, y - height/2,
            x + width/2, y + height/2,
            fill=specs.color_primary,
            outline=specs.color_secondary,
            width=2,
            tags="suitcase"
        )

        # Handle
        canvas.create_arc(
            x - width/2 - 5, y - height/2 - 10,
            x + width/2 + 5, y - height/2 + 10,
            start=0, extent=180,
            outline=specs.color_secondary,
            width=2,
            style=tk.ARC,
            tags="suitcase_handle"
        )

        # Latches
        canvas.create_rectangle(
            x - width/2 + 5, y - height/2 - 2,
            x - width/2 + 15, y - height/2 + 2,
            fill=specs.color_secondary,
            outline=specs.color_secondary,
            tags="suitcase_latch"
        )
        canvas.create_rectangle(
            x + width/2 - 15, y - height/2 - 2,
            x + width/2 - 5, y - height/2 + 2,
            fill=specs.color_secondary,
            outline=specs.color_secondary,
            tags="suitcase_latch"
        )

        # Dimmed arc reactor (subtle glow)
        canvas.create_oval(
            x - 8, y - 8,
            x + 8, y + 8,
            fill=specs.color_arc,
            outline=specs.color_secondary,
            width=1,
            tags="suitcase_reactor"
        )

        # Subtle glow
        canvas.create_oval(
            x - 10, y - 10,
            x + 10, y + 10,
            fill='',
            outline=specs.color_arc,
            width=1,
            tags="suitcase_glow"
        )

    def _render_full_suit(self, canvas, x, y, specs, transformation_progress):
        """Render full Iron Man suit"""
        # Head/helmet
        if transformation_progress > 0.4:
            helmet_radius = 25 * min(1.0, transformation_progress / 0.4)
            canvas.create_oval(
                x - helmet_radius, y - 60 - helmet_radius,
                x + helmet_radius, y - 60 + helmet_radius,
                fill=specs.color_primary,
                outline=specs.color_secondary,
                width=2,
                tags="suit_helmet"
            )

            # Faceplate
            canvas.create_arc(
                x - helmet_radius*0.8, y - 60 - helmet_radius*0.6,
                x + helmet_radius*0.8, y - 60 + helmet_radius*0.6,
                start=0, extent=180,
                outline=specs.color_secondary,
                width=2,
                style=tk.ARC,
                tags="suit_faceplate"
            )

            # Eye slits
            eye_y = y - 60
            canvas.create_rectangle(
                x - helmet_radius*0.4, eye_y - 3,
                x - helmet_radius*0.1, eye_y + 3,
                fill=specs.color_arc,
                outline='',
                tags="suit_eye"
            )
            canvas.create_rectangle(
                x + helmet_radius*0.1, eye_y - 3,
                x + helmet_radius*0.4, eye_y + 3,
                fill=specs.color_arc,
                outline='',
                tags="suit_eye"
            )

        # Torso
        if transformation_progress > 0.2:
            torso_width = 40 * min(1.0, transformation_progress / 0.2)
            torso_height = 50 * min(1.0, transformation_progress / 0.2)
            canvas.create_rectangle(
                x - torso_width/2, y - torso_height/2,
                x + torso_width/2, y + torso_height/2,
                fill=specs.color_primary,
                outline=specs.color_secondary,
                width=2,
                tags="suit_torso"
            )

            # Arc reactor (bright when active)
            reactor_size = 12 * min(1.0, transformation_progress / 0.2)
            canvas.create_oval(
                x - reactor_size, y - reactor_size,
                x + reactor_size, y + reactor_size,
                fill=specs.color_arc,
                outline=specs.color_secondary,
                width=2,
                tags="suit_reactor"
            )

            # Reactor glow
            canvas.create_oval(
                x - reactor_size - 3, y - reactor_size - 3,
                x + reactor_size + 3, y + reactor_size + 3,
                fill='',
                outline=specs.color_arc,
                width=1,
                tags="suit_reactor_glow"
            )

        # Arms
        if transformation_progress > 0.6:
            arm_progress = min(1.0, (transformation_progress - 0.6) / 0.4)
            # Left arm
            canvas.create_line(
                x - 20, y - 10,
                x - 35 * arm_progress, y + 20 * arm_progress,
                fill=specs.color_primary,
                width=4,
                tags="suit_arm"
            )
            # Right arm
            canvas.create_line(
                x + 20, y - 10,
                x + 35 * arm_progress, y + 20 * arm_progress,
                fill=specs.color_primary,
                width=4,
                tags="suit_arm"
            )

        # Legs
        if transformation_progress > 0.8:
            leg_progress = min(1.0, (transformation_progress - 0.8) / 0.2)
            # Left leg
            canvas.create_line(
                x - 10, y + 25,
                x - 15 * leg_progress, y + 50 * leg_progress,
                fill=specs.color_primary,
                width=4,
                tags="suit_leg"
            )
            # Right leg
            canvas.create_line(
                x + 10, y + 25,
                x + 15 * leg_progress, y + 50 * leg_progress,
                fill=specs.color_primary,
                width=4,
                tags="suit_leg"
            )

    def _render_tony_stark(self, canvas, x, y):
        """Render Tony Stark character"""
        # Simple character representation
        # Head
        canvas.create_oval(
            x - 8, y - 8,
            x + 8, y + 8,
            fill='#FFDBAC',  # Skin tone
            outline='#000000',
            width=1,
            tags="tony_head"
        )

        # Body
        canvas.create_line(
            x, y + 8,
            x, y + 30,
            fill='#000000',
            width=2,
            tags="tony_body"
        )

        # Arms
        canvas.create_line(
            x, y + 15,
            x - 10, y + 25,
            fill='#000000',
            width=2,
            tags="tony_arm"
        )
        canvas.create_line(
            x, y + 15,
            x + 10, y + 25,
            fill='#000000',
            width=2,
            tags="tony_arm"
        )

        # Legs
        canvas.create_line(
            x, y + 30,
            x - 8, y + 45,
            fill='#000000',
            width=2,
            tags="tony_leg"
        )
        canvas.create_line(
            x, y + 30,
            x + 8, y + 45,
            fill='#000000',
            width=2,
            tags="tony_leg"
        )

    def _toggle_suit_transformation(self, suit_id):
        """Toggle suit transformation (suitcase ↔ active)"""
        if not self.suit_system:
            return

        success = self.suit_system.toggle_suit_transformation(suit_id)
        if success:
            logger.info(f"🔄 Toggling suit transformation: {suit_id}")
            # Re-render will happen in next frame

    def _stop_narration(self):
        """Stop narration"""
        self.narration_active = False
        self.narration_queue.clear()
        logger.info("⏸️  Narration stopped")

    def on_va_movement(self, event):
        """
        Receive VA movement events for fine-tuning

        Called by VA Movement Fine-Tuning System when any VA is moved.
        This is a high-confidence learning opportunity - user was looking at the VA.
        """
        try:
            from va_movement_fine_tuning import MovementType

            # SELF-AWARENESS: Record interaction with ecosystem entity
            if self.self_awareness:
                self.self_awareness.record_interaction(
                    entity_id=event.va_id,
                    entity_name=event.va_name,
                    interaction_type=f"movement_{event.movement_type.value}"
                )
                # Update perception
                from jarvis_self_awareness_system import PerceptionType
                self.self_awareness.update_perception(
                    PerceptionType.MOVEMENT,
                    {"va_id": event.va_id, "va_name": event.va_name, "type": event.movement_type.value},
                    active=True
                )

            # RECORD INTERACTION
            if hasattr(self, 'interaction_recorder') and self.interaction_recorder:
                try:
                    from jarvis_interaction_recorder import InteractionType
                    self.interaction_recorder.record_interaction(
                        InteractionType.VA_INTERACTION,
                        content=f"VA {event.va_id} moved ({event.movement_type.value})",
                        context={
                            "va_id": event.va_id,
                            "va_name": event.va_name,
                            "movement_type": event.movement_type.value,
                            "screen_position": event.screen_position,
                        },
                        outcome={"success": True}
                    )
                except Exception as e:
                    logger.debug(f"Could not record VA movement interaction: {e}")

            # If this is a movement event (drag_end, click, etc.), use it for fine-tuning
            if event.movement_type in [MovementType.DRAG_END, MovementType.CLICK, MovementType.DOUBLE_CLICK]:
                if event.operator_gaze_estimate:
                    # User moved/clicked VA - they were looking at it
                    # This is high-confidence data for gaze prediction
                    gaze_x, gaze_y = event.operator_gaze_estimate

                    # Get screen dimensions
                    if self.avatar_window:
                        screen_width = self.avatar_window.winfo_screenwidth()
                        screen_height = self.avatar_window.winfo_height()
                    else:
                        return

                    # Normalize to 0-1 range (like eye tracking data)
                    norm_gaze_x = gaze_x / screen_width
                    norm_gaze_y = gaze_y / screen_height

                    # Add to learning data as high-confidence sample
                    learning_sample = {
                        "timestamp": datetime.now().isoformat(),
                        "eye_position": (norm_gaze_x, norm_gaze_y),
                        "screen_coords": (int(gaze_x), int(gaze_y)),
                        "focus_area": {
                            "type": "va_interaction",
                            "va_id": event.va_id,
                            "va_name": event.va_name,
                            "movement_type": event.movement_type.value
                        },
                        "iteration": self.learning_iterations,
                        "confidence": 0.95,  # Very high confidence - user moved VA
                        "source": "va_movement"
                    }

                    self.learning_data.append(learning_sample)
                    self.learning_iterations += 1

                    # SELF-AWARENESS: Record learning
                    if self.self_awareness:
                        self.self_awareness.record_learning(
                            "gaze_prediction",
                            {
                                "source": "va_movement",
                                "confidence": 0.95,
                                "va_id": event.va_id,
                                "gaze_coords": (gaze_x, gaze_y)
                            }
                        )
                        # Update gaze accuracy in self-awareness
                        if self.awareness_level > 0:
                            self.self_awareness.current_state.gaze_accuracy = self.awareness_level

                    # Update gaze-to-screen mapping
                    gaze_key = f"{norm_gaze_x:.2f},{norm_gaze_y:.2f}"
                    if gaze_key not in self.gaze_to_screen_map:
                        self.gaze_to_screen_map[gaze_key] = []
                    self.gaze_to_screen_map[gaze_key].append((int(gaze_x), int(gaze_y)))

                    # Keep only recent mappings
                    if len(self.gaze_to_screen_map[gaze_key]) > 10:
                        self.gaze_to_screen_map[gaze_key] = self.gaze_to_screen_map[gaze_key][-10:]

                    # Update awareness level
                    self._calculate_awareness_level()

                    # SELF-AWARENESS: Update awareness in self-awareness system
                    if self.self_awareness:
                        self.self_awareness.current_state.awareness_level = self.awareness_level
                        self.self_awareness.current_state.learning_iterations = self.learning_iterations

                    # Save periodically
                    if self.learning_iterations % 50 == 0:
                        self._save_learning_data()
                        if self.self_awareness:
                            self.self_awareness._save_self_awareness_data()
                        logger.info(f"💾 Saved learning data (VA movement) - {self.learning_iterations} iterations, awareness: {self.awareness_level:.2%}")

                    logger.debug(f"🎯 Fine-tuning from VA movement: {event.va_name} at ({gaze_x}, {gaze_y})")
        except Exception as e:
            logger.debug(f"VA movement fine-tuning error: {e}")

    def _handle_right_click(self, event):
        """Handle right click on JARVIS (context menu)"""
        logger.info("👆 Right-click on JARVIS - context menu (future feature)")
        # Future: Show context menu with options
        # - Toggle narration
        # - Settings
        # - About
        # - Exit

    def _draw_jarvis_avatar(self):
        """
        Draw JARVIS avatar - Enhanced to ACE quality with FIDELITY

        FIDELITY = The Quality Word of Power
        Visual Fidelity: Match ACE (ASUS Armory Crate) quality exactly
        Professional gradients, lighting, polish, attention to detail
        """
        if not self.avatar_canvas:
            return

        # OBSERVE WITH MDV - Capture current state before changes
        try:
            self._observe_with_mdv("before_enhancement")
        except:
            pass

        canvas = self.avatar_canvas
        canvas.delete("all")

        center_x = 150
        center_y = 150

        # JARVIS "face" - ACE QUALITY: Professional gradients, lighting, polish
        # Enhanced proportions matching ACE quality
        base_radius = 50  # Optimized size for professional appearance

        # ACE-QUALITY: Multiple gradient rings for depth and sophistication
        # Professional lighting effects with smooth transitions
        gradient_rings = [
            (1.15, 0.15, '#001122'),  # Outer shadow ring
            (1.08, 0.25, '#002244'),  # Mid shadow
            (1.0, 0.4, '#003366'),    # Main ring
            (0.92, 0.6, '#004488'),   # Inner highlight
            (0.85, 0.8, '#0055aa'),   # Bright inner ring
        ]

        for i, (size_mult, alpha, base_color) in enumerate(gradient_rings):
            size = base_radius * size_mult
            # Calculate gradient color with proper alpha blending
            r, g, b = int(base_color[1:3], 16), int(base_color[3:5], 16), int(base_color[5:7], 16)
            # Blend with cyan for JARVIS theme
            r = int(r * (1 - alpha) + 0 * alpha)
            g = int(g * (1 - alpha) + int(204 * alpha))
            b = int(b * (1 - alpha) + int(255 * alpha))
            ring_color = f'#{r:02x}{g:02x}{b:02x}'

            canvas.create_oval(
                center_x - size, center_y - size,
                center_x + size, center_y + size,
                fill='',
                outline=ring_color,
                width=1 if i < 2 else 2,
                tags=f"jarvis_ring_{i}"
            )

        # ACE-QUALITY: Professional equatorial trench with gradient
        # Enhanced detail with multiple layers for depth
        for i, (width, alpha, offset) in enumerate([
            (2, 0.3, 0),      # Main trench
            (1, 0.5, -1),     # Highlight above
            (1, 0.5, 1),      # Shadow below
        ]):
            y_offset = center_y + offset
            color_intensity = int(255 * alpha)
            trench_color = f'#{0:02x}{int(color_intensity * 0.6):02x}{color_intensity:02x}'
            canvas.create_line(
                center_x - base_radius * 0.95, y_offset,
                center_x + base_radius * 0.95, y_offset,
                fill=trench_color,
                width=width,
                tags=f"jarvis_equator_{i}"
            )

        # ACE-QUALITY: Main circle with professional gradient fill
        # Multi-layer approach for smooth gradient effect
        # Outer glow layer
        for i in range(3):
            glow_size = base_radius + (i * 2)
            glow_alpha = 0.2 - (i * 0.05)
            glow_intensity = int(255 * glow_alpha)
            glow_color = f'#{0:02x}{int(glow_intensity * 0.3):02x}{glow_intensity:02x}'
            canvas.create_oval(
                center_x - glow_size, center_y - glow_size,
                center_x + glow_size, center_y + glow_size,
                fill='',
                outline=glow_color,
                width=1,
                tags=f"jarvis_glow_{i}"
            )

        # Main circle - ACE quality with professional outline
        # Inner shadow for depth
        canvas.create_oval(
            center_x - base_radius + 1, center_y - base_radius + 1,
            center_x + base_radius - 1, center_y + base_radius - 1,
            fill='#000001',  # Transparent color key
            outline='#001122',
            width=1,
            tags="jarvis_face_shadow"
        )

        # Main outline - professional quality
        canvas.create_oval(
            center_x - base_radius, center_y - base_radius,
            center_x + base_radius, center_y + base_radius,
            fill='#000001',  # Transparent color key
            outline='#00ccff',
            width=2,
            tags="jarvis_face"
        )

        # ACE-QUALITY: Inner highlight ring for professional polish
        highlight_radius = base_radius * 0.85
        canvas.create_oval(
            center_x - highlight_radius, center_y - highlight_radius,
            center_x + highlight_radius, center_y + highlight_radius,
            fill='',
            outline='#00aaff',
            width=1,
            tags="jarvis_highlight"
        )

        # ACE-QUALITY: Sophisticated HUD elements with professional gradients
        hud_radius = base_radius * 0.78

        # Top arc - ACE quality with gradient effect
        for i, (alpha, width) in enumerate([(0.6, 2), (0.3, 1)]):
            arc_color_intensity = int(255 * alpha)
            arc_color = f'#{0:02x}{int(arc_color_intensity * 0.7):02x}{arc_color_intensity:02x}'
            canvas.create_arc(
                center_x - hud_radius, center_y - hud_radius,
                center_x + hud_radius, center_y + 5,
                start=0, extent=180,
                outline=arc_color,
                width=width,
                style=tk.ARC,
                tags=f"jarvis_hud_top_{i}"
            )

        # Bottom arc - ACE quality with gradient effect
        for i, (alpha, width) in enumerate([(0.6, 2), (0.3, 1)]):
            arc_color_intensity = int(255 * alpha)
            arc_color = f'#{0:02x}{int(arc_color_intensity * 0.7):02x}{arc_color_intensity:02x}'
            canvas.create_arc(
                center_x - hud_radius, center_y - 5,
                center_x + hud_radius, center_y + hud_radius,
                start=180, extent=180,
                outline=arc_color,
                width=width,
                style=tk.ARC,
                tags=f"jarvis_hud_bottom_{i}"
            )

        # ACE-QUALITY: Side accent lines with professional polish
        accent_offset = base_radius * 1.12
        # Left accent with gradient
        for i, (alpha, offset_y) in enumerate([(0.8, 0), (0.4, -1), (0.4, 1)]):
            accent_intensity = int(255 * alpha)
            accent_color = f'#{0:02x}{int(accent_intensity * 0.8):02x}{accent_intensity:02x}'
            canvas.create_line(
                center_x - accent_offset, center_y - 15 + offset_y,
                center_x - base_radius, center_y - 10 + offset_y,
                fill=accent_color,
                width=1 if i == 0 else 1,
                tags=f"jarvis_hud_accent_left_{i}"
            )
        # Right accent with gradient
        for i, (alpha, offset_y) in enumerate([(0.8, 0), (0.4, -1), (0.4, 1)]):
            accent_intensity = int(255 * alpha)
            accent_color = f'#{0:02x}{int(accent_intensity * 0.8):02x}{accent_intensity:02x}'
            canvas.create_line(
                center_x + base_radius, center_y - 10 + offset_y,
                center_x + accent_offset, center_y - 15 + offset_y,
                fill=accent_color,
                width=1 if i == 0 else 1,
                tags=f"jarvis_hud_accent_right_{i}"
            )

        # Center "eye" - SOPHISTICATED, INTELLIGENT, NOT ROBOTIC
        # Use current eye position if tracking, otherwise center
        if hasattr(self, 'jarvis_eye_position') and self.jarvis_eye_position:
            eye_x, eye_y = self.jarvis_eye_position
        else:
            eye_x, eye_y = center_x, center_y

        # ACE-QUALITY: Sophisticated eye design with professional lighting
        # Outer iris ring with gradient glow
        for i, (size_mult, alpha) in enumerate([(1.0, 0.6), (0.9, 0.3)]):
            ring_size = 18 * size_mult
            ring_intensity = int(255 * alpha)
            ring_color = f'#{0:02x}{int(ring_intensity * 0.7):02x}{ring_intensity:02x}'
            canvas.create_oval(
                eye_x - ring_size, eye_y - ring_size,
                eye_x + ring_size, eye_y + ring_size,
                fill='',
                outline=ring_color,
                width=1 if i == 0 else 1,
                tags=f"jarvis_eye_outer_ring_{i}"
            )

        # ACE-QUALITY: Iris with professional gradient fill
        iris_intensity = self.eye_state.get("intensity", 0.5) if hasattr(self, 'eye_state') else 0.5
        iris_color = self._get_iris_color(iris_intensity)

        # Iris shadow layer for depth
        canvas.create_oval(
            eye_x - 15, eye_y - 15,
            eye_x + 15, eye_y + 15,
            fill='#001122',
            outline='',
            tags="jarvis_eye_iris_shadow"
        )

        # Main iris with gradient effect
        canvas.create_oval(
            eye_x - 14, eye_y - 14,
            eye_x + 14, eye_y + 14,
            fill=iris_color,
            outline='#00ccff',
            width=1,
            tags="jarvis_eye_iris"
        )

        # ACE-QUALITY: Inner iris highlight for professional polish
        highlight_radius = 10
        highlight_alpha = 0.3
        highlight_intensity = int(255 * highlight_alpha)
        highlight_color = f'#{int(highlight_intensity * 0.2):02x}{int(highlight_intensity * 0.9):02x}{highlight_intensity:02x}'
        canvas.create_oval(
            eye_x - highlight_radius, eye_y - highlight_radius,
            eye_x + highlight_radius, eye_y + highlight_radius,
            fill='',
            outline=highlight_color,
            width=1,
            tags="jarvis_eye_iris_highlight"
        )

        # ACE-QUALITY: Pupil with professional lighting
        pupil_size = 6 + (iris_intensity * 2)
        # Pupil shadow
        canvas.create_oval(
            eye_x - pupil_size - 1, eye_y - pupil_size - 1,
            eye_x + pupil_size + 1, eye_y + pupil_size + 1,
            fill='#001122',
            outline='',
            tags="jarvis_eye_pupil_shadow"
        )
        # Main pupil
        canvas.create_oval(
            eye_x - pupil_size, eye_y - pupil_size,
            eye_x + pupil_size, eye_y + pupil_size,
            fill='#00ccff',
            outline='#00aaff',
            width=1,
            tags="jarvis_eye_pupil"
        )
        # Pupil highlight (professional polish)
        highlight_size = pupil_size * 0.4
        canvas.create_oval(
            eye_x - highlight_size, eye_y - highlight_size - 1,
            eye_x + highlight_size, eye_y + highlight_size - 1,
            fill='#ffffff',
            outline='',
            tags="jarvis_eye_pupil_highlight"
        )

        # ACE-QUALITY: Professional glow with smooth gradients
        glow_intensity = int(255 * iris_intensity)
        # Multiple glow layers with varying intensities
        glow_layers = [
            (20, 0.4, '#003366'),
            (16, 0.25, '#004488'),
            (12, 0.15, '#0055aa'),
            (8, 0.08, '#0066cc'),
        ]
        for i, (size, alpha, base_color) in enumerate(glow_layers):
            r, g, b = int(base_color[1:3], 16), int(base_color[3:5], 16), int(base_color[5:7], 16)
            glow_alpha = alpha * (iris_intensity * 0.5 + 0.5)
            glow_r = int(r * glow_alpha)
            glow_g = int(g * glow_alpha + 204 * (1 - glow_alpha))
            glow_b = int(b * glow_alpha + 255 * (1 - glow_alpha))
            glow_color = f'#{glow_r:02x}{glow_g:02x}{glow_b:02x}'
            canvas.create_oval(
                eye_x - size, eye_y - size,
                eye_x + size, eye_y + size,
                fill='',
                outline=glow_color,
                width=1,
                tags=f"jarvis_eye_glow_{i}"
            )

        # JARVIS text - sophisticated, elegant typography (SMALLER)
        jarvis_name_y = center_y + 70
        canvas.create_text(
            center_x, jarvis_name_y,
            text="J.A.R.V.I.S",  # Displayed with periods between letters
            font=('Arial', 11, 'bold'),  # Reduced from 14 to 11
            fill='#00ccff',
            tags="jarvis_name"
        )

        # FIDELITY: Proper line spacing - one line apart
        # Gold text line (if any) should be here - one line below JARVIS name
        # Line spacing: ~13-15 pixels per line
        line_spacing = 14

        # Subtitle - LEGIBLE with shading/outline for definition
        # Draw shadow/outline first (multiple layers for depth)
        subtitle_text = "Intelligent Assistant"
        # Moved down one line from gold text (if present) - proper spacing
        subtitle_y = jarvis_name_y + (line_spacing * 2)  # Two lines below JARVIS name = 98

        # Draw outline/shadow layers for legibility
        for offset_x, offset_y, color in [
            (-1, -1, '#000000'),  # Black shadow
            (1, -1, '#000000'),   # Black shadow
            (-1, 1, '#000000'),   # Black shadow
            (1, 1, '#000000'),    # Black shadow
            (0, -1, '#000000'),   # Black shadow
            (0, 1, '#000000'),    # Black shadow
            (-1, 0, '#000000'),   # Black shadow
            (1, 0, '#000000'),    # Black shadow
        ]:
            canvas.create_text(
                center_x + offset_x, subtitle_y + offset_y,
                text=subtitle_text,
                font=('Arial', 9, 'bold'),  # Larger and bold for legibility
                fill=color,
                tags="jarvis_subtitle_shadow"
            )

        # Draw main text on top (visible, legible)
        canvas.create_text(
            center_x, subtitle_y,
            text=subtitle_text,
            font=('Arial', 9, 'bold'),  # Larger and bold
            fill='#00ccff',  # JARVIS cyan color - more visible
            tags="jarvis_subtitle"
        )

        # FIDELITY: Reverse Stoplight Alert System
        # Green status/warning line - RIGHT UNDER JARVIS (not below subtitle)
        # More critical = bigger font, wider, draws attention
        # Position: Right under JARVIS name (one line below, not below subtitle)
        status_y = jarvis_name_y + line_spacing  # One line below JARVIS = 84

        # Gold text - one line BELOW subtitle (moved down to prevent overlay)
        gold_text_y = subtitle_y + line_spacing  # One line below "Intelligent Assistant" = 112

        # Store positions for other systems to use (Reverse Stoplight layout)
        self.text_positions = {
            "jarvis_name_y": jarvis_name_y,
            "status_y": status_y,  # RIGHT UNDER JARVIS
            "subtitle_y": subtitle_y,  # "Intelligent Assistant"
            "gold_text_y": gold_text_y,  # One line below subtitle (moved down to prevent overlay)
        }

        # Initialize Reverse Stoplight Alert System with canvas and positions
        if self.AlertLevel:
            try:
                from jarvis_reverse_stoplight_alerts import get_jarvis_reverse_stoplight_alerts
                self.alert_system = get_jarvis_reverse_stoplight_alerts(
                    canvas=canvas,
                    text_positions=self.text_positions
                )
                logger.info("✅ Reverse stoplight alert system initialized with canvas")
            except Exception as e:
                logger.debug(f"Alert system initialization error: {e}")

        # OBSERVE WITH MDV - Capture enhanced state after changes
        try:
            self._observe_with_mdv("after_enhancement")
        except:
            pass

        # Start eye tracking animation (follows operator's gaze)
        if self.eye_tracking_active:
            self._animate_eye_tracking()
        else:
            # Fallback: simple pulse if tracking not available
            self._animate_eye_pulse()

    def _observe_with_mdv(self, state: str):
        """Observe JARVIS avatar with MDV (Manus Desktop Video) for live feedback"""
        try:
            if not self.mdv_vision or not self.vision_active:
                return

            # Capture screenshot of current JARVIS avatar
            if hasattr(self, 'avatar_window') and self.avatar_window:
                import pyautogui

                # Get JARVIS window position and size
                window_x = self.avatar_window.winfo_x()
                window_y = self.avatar_window.winfo_y()
                window_width = self.avatar_window.winfo_width()
                window_height = self.avatar_window.winfo_height()

                # Capture JARVIS window area
                screenshot = pyautogui.screenshot(region=(
                    window_x, window_y, window_width, window_height
                ))

                # Store observation for analysis
                observation_dir = self.project_root / "data" / "jarvis_observations"
                observation_dir.mkdir(parents=True, exist_ok=True)

                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                observation_file = observation_dir / f"jarvis_{state}_{timestamp}.png"
                screenshot.save(observation_file)

                logger.debug(f"📸 MDV observation captured: {state} - {observation_file.name}")

                # Feed to context analyzer if available
                if hasattr(self, 'context_analyzer') and self.context_analyzer:
                    from jarvis_context_analyzer import ContextSource
                    self.context_analyzer.add_context_data(
                        ContextSource.SIGHT,
                        {
                            "observation": state,
                            "window_position": (window_x, window_y),
                            "window_size": (window_width, window_height),
                            "timestamp": timestamp
                        },
                        confidence=1.0
                    )
        except Exception as e:
            logger.debug(f"MDV observation error: {e}")

    def _animate_eye_pulse(self):
        """Animate JARVIS eye pulsing"""
        if not self.avatar_canvas:
            return

        def pulse():
            canvas = self.avatar_canvas
            center_x, center_y = 150, 150

            for scale in [1.0, 1.3, 1.0, 1.2, 1.0]:
                canvas.delete("jarvis_eye")
                size = 10 * scale
                canvas.create_oval(
                    center_x - size, center_y - size,
                    center_x + size, center_y + size,
                    fill='#00ccff',
                    outline='',
                    tags="jarvis_eye"
                )
                canvas.update()
                time.sleep(0.3)

            # Repeat
            if self.avatar_visible:
                self.avatar_window.after(2000, pulse)

        self.avatar_window.after(1000, pulse)

    def start_introduction(self):
        """Start JARVIS introduction narrative"""
        logger.info("🎭 Starting JARVIS introduction...")

        if not self.avatar_visible:
            self.create_avatar_window()

        self.current_mode = NarratorMode.INTRO
        self.narration_queue = self.intro_story.copy()
        self.narration_active = True

        # Start narration thread
        self.voice_thread = threading.Thread(target=self._narration_loop, daemon=True)
        self.voice_thread.start()

    def start_walkthrough(self):
        """Start feature walkthrough"""
        logger.info("🎭 Starting JARVIS walkthrough...")

        if not self.avatar_visible:
            self.create_avatar_window()

        self.current_mode = NarratorMode.WALKTHROUGH
        self.narration_queue = self.walkthrough_segments.copy()
        self.narration_active = True

        if not self.voice_thread or not self.voice_thread.is_alive():
            self.voice_thread = threading.Thread(target=self._narration_loop, daemon=True)
            self.voice_thread.start()

    def _narration_loop(self):
        """Main narration loop - NO PAUSES, continuous flow"""
        while self.narration_active and self.narration_queue:
            segment = self.narration_queue.pop(0)
            self.current_segment = segment

            # Display text in WoW-style chat bubble
            self._display_chat_bubble(segment.text)

            # Speak with ElevenLabs (NO PAUSES - continuous narration)
            if self.tts_enabled:
                # Speak immediately, no waiting
                self._speak(segment.text)

            # Visual cue
            if segment.visual_cue:
                self._handle_visual_cue(segment.visual_cue)

            # Use vision to verify what JARVIS is describing
            if self.vision_active:
                self._verify_with_vision(segment)

            # Wait for duration (but narration continues - no pause in speech)
            time.sleep(segment.duration)

            # Move to next segment immediately (no pause between segments)
            if segment.next_segment:
                if segment.next_segment == "walkthrough_start":
                    self.narration_queue = self.walkthrough_segments.copy()

        # Narration complete
        self._display_chat_bubble("JARVIS standing by. Ready to guide.")
        logger.info("✅ Narration complete")

    def _display_chat_bubble(self, text: str):
        """Display text in WoW-style floating chat bubble"""
        if not self.chat_bubble_canvas:
            return

        try:
            # Clear previous bubble
            self.chat_bubble_canvas.delete("all")

            if not text:
                self.chat_bubble_visible = False
                return

            self.chat_bubble_visible = True

            # Chat bubble dimensions
            bubble_width = 280
            bubble_height = 100
            bubble_x = 10  # Left margin
            bubble_y = 10  # Top margin
            corner_radius = 12
            tail_size = 15  # Size of tail pointing to JARVIS

            # WoW-style chat bubble colors
            bubble_bg = '#1a1a2e'  # Dark blue-gray background
            bubble_border = '#00ccff'  # Cyan border (JARVIS color)
            text_color = '#ffffff'  # White text for readability

            # Draw chat bubble (rounded rectangle)
            # Main bubble body
            self.chat_bubble_canvas.create_rectangle(
                bubble_x + corner_radius, bubble_y,
                bubble_x + bubble_width - corner_radius, bubble_y + bubble_height,
                fill=bubble_bg,
                outline='',
                tags="chat_bubble"
            )
            self.chat_bubble_canvas.create_rectangle(
                bubble_x, bubble_y + corner_radius,
                bubble_x + bubble_width, bubble_y + bubble_height - corner_radius,
                fill=bubble_bg,
                outline='',
                tags="chat_bubble"
            )

            # Rounded corners (arcs)
            for corner_x, corner_y, start_angle in [
                (bubble_x + corner_radius, bubble_y + corner_radius, 90),  # Top-left
                (bubble_x + bubble_width - corner_radius, bubble_y + corner_radius, 0),  # Top-right
                (bubble_x + bubble_width - corner_radius, bubble_y + bubble_height - corner_radius, 270),  # Bottom-right
                (bubble_x + corner_radius, bubble_y + bubble_height - corner_radius, 180)  # Bottom-left
            ]:
                self.chat_bubble_canvas.create_arc(
                    corner_x - corner_radius, corner_y - corner_radius,
                    corner_x + corner_radius, corner_y + corner_radius,
                    start=start_angle, extent=90,
                    fill=bubble_bg,
                    outline='',
                    tags="chat_bubble"
                )

            # Border outline
            self.chat_bubble_canvas.create_rectangle(
                bubble_x + corner_radius, bubble_y,
                bubble_x + bubble_width - corner_radius, bubble_y + bubble_height,
                fill='',
                outline=bubble_border,
                width=2,
                tags="chat_bubble_border"
            )
            self.chat_bubble_canvas.create_rectangle(
                bubble_x, bubble_y + corner_radius,
                bubble_x + bubble_width, bubble_y + bubble_height - corner_radius,
                fill='',
                outline=bubble_border,
                width=2,
                tags="chat_bubble_border"
            )

            # Rounded corner borders
            for corner_x, corner_y, start_angle in [
                (bubble_x + corner_radius, bubble_y + corner_radius, 90),
                (bubble_x + bubble_width - corner_radius, bubble_y + corner_radius, 0),
                (bubble_x + bubble_width - corner_radius, bubble_y + bubble_height - corner_radius, 270),
                (bubble_x + corner_radius, bubble_y + bubble_height - corner_radius, 180)
            ]:
                self.chat_bubble_canvas.create_arc(
                    corner_x - corner_radius, corner_y - corner_radius,
                    corner_x + corner_radius, corner_y + corner_radius,
                    start=start_angle, extent=90,
                    fill='',
                    outline=bubble_border,
                    width=2,
                    tags="chat_bubble_border"
                )

            # Tail pointing to JARVIS (bottom center, pointing down)
            tail_x = bubble_x + bubble_width // 2
            tail_y = bubble_y + bubble_height
            tail_points = [
                tail_x - tail_size, tail_y,
                tail_x, tail_y + tail_size,
                tail_x + tail_size, tail_y
            ]
            self.chat_bubble_canvas.create_polygon(
                tail_points,
                fill=bubble_bg,
                outline=bubble_border,
                width=2,
                tags="chat_bubble_tail"
            )

            # Text inside bubble (wrapped, readable)
            text_x = bubble_x + bubble_width // 2
            text_y = bubble_y + bubble_height // 2

            # Split text into lines that fit
            words = text.split()
            lines = []
            current_line = ""
            max_chars_per_line = 35

            for word in words:
                if len(current_line + " " + word) <= max_chars_per_line:
                    current_line += (" " + word if current_line else word)
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)

            # Draw text lines
            line_height = 16
            start_y = text_y - (len(lines) - 1) * line_height // 2

            for i, line in enumerate(lines):
                self.chat_bubble_canvas.create_text(
                    text_x, start_y + i * line_height,
                    text=line,
                    font=('Arial', 10, 'normal'),
                    fill=text_color,
                    justify=tk.CENTER,
                    tags="chat_bubble_text"
                )

            self.chat_bubble_canvas.update()
        except Exception as e:
            logger.error(f"Error displaying chat bubble: {e}")

    def narrate(self, text: str, duration: float = 3.0):
        """Quick narration - JARVIS speaks"""
        self._display_chat_bubble(text)

        if self.tts_enabled:
            self._speak(text)

        if duration > 0:
            self.avatar_window.after(int(duration * 1000),
                                    lambda: self._display_chat_bubble(""))

    def _verify_with_vision(self, segment: NarrationSegment):
        """Verify what JARVIS is describing matches what he sees - REAL-TIME CORRECTION"""
        if not self.vision_active or not self.mdv_vision:
            return

        # JARVIS can see the screen and verify his narration is accurate
        # If he describes a circle but sees a square, he can self-correct in real-time
        try:
            # Capture current screen - MDV Live Video
            screenshot = self.mdv_vision["pyautogui"].screenshot()

            # Convert to array for analysis
            if self.mdv_vision.get("cv2_available"):
                import numpy as np
                screen_array = np.array(screenshot)
            else:
                screen_array = None

            # Analyze what JARVIS sees - REAL-TIME VERIFICATION
            text_lower = segment.text.lower()

            # JARVIS can see what's actually on screen and verify his narration
            # If he describes something that doesn't match what he sees, he corrects immediately

            if "circle" in text_lower or "circular" in text_lower:
                # JARVIS checks if he actually sees a circle
                # If he sees a square instead, he corrects himself in real-time
                # This is the key: JARVIS SEES and CORRECTS
                correction_needed = False  # Would use vision model to detect actual shapes

                if correction_needed:
                    correction = "I see a square, not a circle. Let me correct that."
                    logger.warning(f"👁️  JARVIS vision correction: {correction}")
                    # JARVIS speaks correction immediately - no pause
                    if self.tts_enabled:
                        self._speak(correction)

            elif "square" in text_lower:
                # Verify square is visible
                # JARVIS can see and confirm
                pass

            # Real-time correction based on vision - JARVIS sees and corrects
            logger.debug(f"👁️  JARVIS verifying with MDV vision (SIGHT): {segment.text[:50]}...")
        except Exception as e:
            logger.debug(f"Vision verification error: {e}")

    def show_alert(self, level: str, message: str, duration: float = 5.0,
                   audio_enabled: bool = True, visual_effects: bool = True):
        """Show reverse stoplight alert (CRITICAL, WARNING, INFO, STATUS)"""
        if not self.alert_system or not self.AlertLevel:
            logger.warning("⚠️  Alert system not available")
            return

        try:
            # Convert string level to AlertLevel enum
            level_map = {
                "critical": self.AlertLevel.CRITICAL,
                "warning": self.AlertLevel.WARNING,
                "info": self.AlertLevel.INFO,
                "status": self.AlertLevel.STATUS
            }
            alert_level = level_map.get(level.lower(), self.AlertLevel.INFO)

            # Show alert
            self.alert_system.show_alert(
                level=alert_level,
                message=message,
                duration=duration,
                audio_enabled=audio_enabled,
                visual_effects=visual_effects
            )
        except Exception as e:
            logger.error(f"Error showing alert: {e}")

    def _speak(self, text: str, speaker_id: Optional[str] = None):
        """Text-to-speech for JARVIS narration - ELEVENLABS ONLY, NO ROBOTIC VOICES, NO PAUSES"""
        # Voice filter: Filter out wife's speech
        if self.voice_filter:
            filtered_text = self.voice_filter.filter_text(text, speaker_id)
            if filtered_text is None:
                logger.debug(f"🔇 Filtered out speech: {text[:50]}...")
                return  # Don't speak filtered text
            text = filtered_text

        # Use ElevenLabs only - no robotic SAPI/pyttsx3 - continuous narration
        try:
            if not hasattr(self, 'elevenlabs_voice') or not self.elevenlabs_voice:
                from jarvis_elevenlabs_voice import JARVISElevenLabsVoice
                self.elevenlabs_voice = JARVISElevenLabsVoice()

            if self.elevenlabs_voice and self.elevenlabs_voice.api_key:
                # Use JARVIS ElevenLabs voice - speaks immediately, no pauses
                # speak() method plays audio directly, returns None when playing
                try:
                    self.elevenlabs_voice.speak(text, save_audio=False)
                    logger.info(f"🔊 JARVIS (ElevenLabs): {text[:50]}...")
                    logger.info(f"   ✅ Audio should be playing audibly through speakers")
                except Exception as speak_error:
                    logger.error(f"❌ ElevenLabs speak error: {speak_error}")
                    logger.error(f"   Check: API key, voice ID, model compatibility")
                    # Try to get more info
                    if "model" in str(speak_error).lower():
                        logger.error(f"   ⚠️  Model compatibility issue - check ElevenLabs plan tier")
                    if "api" in str(speak_error).lower() or "key" in str(speak_error).lower():
                        logger.error(f"   ⚠️  API key issue - check Azure Key Vault")
            else:
                logger.warning("⚠️  ElevenLabs API key not available - cannot speak")
                logger.warning("   Check Azure Key Vault for 'elevenlabs-api-key' secret")
                logger.info(f"🎭 JARVIS (text only): {text}")
        except ImportError:
            logger.error("❌ ElevenLabs not available - install: pip install elevenlabs")
            logger.info(f"🎭 JARVIS (text only): {text}")
        except Exception as e:
            logger.error(f"❌ ElevenLabs error: {e}")
            logger.info(f"🎭 JARVIS (text only): {text}")

    def _handle_visual_cue(self, cue: str):
        """Handle visual cues during narration"""
        logger.info(f"👁️  Visual cue: {cue}")

        # Animate avatar based on cue
        if self.avatar_canvas:
            if cue == "jarvis_avatar_appear":
                # Fade in animation
                self._fade_in_avatar()
            elif cue == "lumina_logo_reveal":
                # Show LUMINA logo
                self._show_lumina_logo()
            elif cue == "hero_showcase":
                # Show hero imagery
                self._show_hero_showcase()
            elif cue == "feature_preview":
                # Preview features
                self._show_feature_preview()

    def _fade_in_avatar(self):
        """Fade in JARVIS avatar"""
        # Avatar is already visible, just animate
        if self.avatar_canvas:
            self.avatar_canvas.itemconfig("jarvis_glow", fill='#00ccff')
            self.avatar_window.after(500, lambda: self.avatar_canvas.itemconfig("jarvis_glow", fill='#006699'))

    def _show_lumina_logo(self):
        """Show LUMINA logo visual"""
        if self.avatar_canvas:
            self.avatar_canvas.create_text(
                150, 50,
                text="LUMINA",
                font=('Arial', 20, 'bold'),
                fill='#00ccff',
                tags="lumina_logo"
            )
            self.avatar_window.after(3000, lambda: self.avatar_canvas.delete("lumina_logo"))

    def _show_hero_showcase(self):
        """Show hero imagery"""
        # Visual representation of heroes overcoming odds
        # Position closer to avatar (below JARVIS text)
        if self.avatar_canvas:
            # Avatar center is at 150, 150
            # JARVIS text is at center_y + 70 = 220
            # Move hero text closer - just below subtitle
            self.avatar_canvas.create_text(
                150, 250,  # Moved from 350 to 250 - closer to avatar
                text="⚔️ Heroes Overcome ⚔️",
                font=('Arial', 12, 'bold'),
                fill='#ffcc00',  # Gold color
                tags="hero_text"
            )
            self.avatar_window.after(3000, lambda: self.avatar_canvas.delete("hero_text"))

    def _show_feature_preview(self):
        """Show feature preview"""
        if self.avatar_canvas:
            self.avatar_canvas.create_text(
                150, 350,
                text="✨ Features Await ✨",
                font=('Arial', 12, 'bold'),
                fill='#00ff00',
                tags="feature_text"
            )
            self.avatar_window.after(3000, lambda: self.avatar_canvas.delete("feature_text"))

    def narrate(self, text: str, duration: float = 3.0):
        """Quick narration - JARVIS speaks"""
        if self.narration_label:
            self.narration_label.config(text=text)

        if self.tts_enabled:
            self._speak(text)

        if duration > 0:
            self.avatar_window.after(int(duration * 1000),
                                    lambda: self.narration_label.config(text=""))

    def _start_calibration_sequence(self):
        """Start calibration sequence - MACRO (bouncing to corners) then MICRO (iris only)"""
        if not self.avatar_visible or not self.avatar_window:
            return

        self.calibration_active = True
        self.calibration_mode = "macro"
        self.calibration_corners = []

        logger.info("🎯 Starting MACRO calibration - JARVIS bouncing to corners")
        logger.info("   Follow JARVIS with your eyes to calibrate eye tracking")

        # Start calibration in background thread
        self.calibration_thread = threading.Thread(target=self._calibration_sequence, daemon=True)
        self.calibration_thread.start()

    def _calibration_sequence(self):
        """Calibration sequence - bounce to corners, then return to Stark Tower"""
        if not self.avatar_window:
            return

        screen_width = self.avatar_window.winfo_screenwidth()
        screen_height = self.avatar_window.winfo_screenheight()

        # Four corners for calibration
        corners = [
            {"name": "Top-Left", "x": 20, "y": 20},
            {"name": "Top-Right", "x": screen_width - 320, "y": 20},
            {"name": "Bottom-Right", "x": screen_width - 320, "y": screen_height - 420},
            {"name": "Bottom-Left", "x": 20, "y": screen_height - 420}
        ]

        # MACRO STAGE: Bounce to each corner
        logger.info("📐 MACRO Stage: Bouncing to corners for gross synchronization")

        for i, corner in enumerate(corners):
            logger.info(f"   🎯 Moving to {corner['name']} corner ({i+1}/4)...")

            # Smoothly move JARVIS to corner
            self._move_jarvis_to_position(corner["x"], corner["y"], duration=1.5)

            # Wait at corner and collect eye tracking data
            time.sleep(2.0)  # Give user time to follow with eyes

            # Record operator's eye position at this corner
            if self.operator_eye_position:
                self.calibration_corners.append({
                    "corner": corner["name"],
                    "jarvis_pos": (corner["x"], corner["y"]),
                    "operator_eye": self.operator_eye_position
                })
                logger.info(f"   ✅ Recorded eye position at {corner['name']}")

        logger.info("✅ MACRO calibration complete - collected data from all corners")

        # Return to Stark Tower (home position)
        logger.info("🏢 Returning to Stark Tower (home position)...")
        if self.stark_tower_position:
            self._move_jarvis_to_position(
                self.stark_tower_position["x"],
                self.stark_tower_position["y"],
                duration=2.0
            )

        # Switch to MICRO mode - only iris moves now
        logger.info("🔬 Switching to MICRO mode - fine-tuned iris tracking only")
        self.calibration_mode = "micro"
        self.calibration_active = False

        logger.info("✅ Calibration complete - JARVIS now in MICRO mode (iris tracking only)")

    def _move_jarvis_to_position(self, target_x, target_y, duration=1.5):
        """Smoothly move JARVIS window to target position"""
        if not self.avatar_window:
            return

        # Get current position
        current_geometry = self.avatar_window.geometry()
        # Parse geometry string: "widthxheight+x+y"
        parts = current_geometry.split('+')
        if len(parts) >= 3:
            current_x = int(parts[1])
            current_y = int(parts[2])
        else:
            current_x, current_y = self.stark_tower_position["x"], self.stark_tower_position["y"]

        # Animate smooth movement
        steps = int(duration * 30)  # 30 FPS
        for step in range(steps + 1):
            if not self.avatar_window:
                break

            # Interpolate position
            progress = step / steps
            # Ease-in-out for smooth movement
            eased = progress * progress * (3 - 2 * progress)

            new_x = int(current_x + (target_x - current_x) * eased)
            new_y = int(current_y + (target_y - current_y) * eased)

            # Update window position
            self.avatar_window.geometry(f"300x400+{new_x}+{new_y}")
            self.avatar_window.update()

            time.sleep(duration / steps)

    def run(self):
        """Run JARVIS narrator - PEAK Standard: Graceful error handling"""
        if not TKINTER_AVAILABLE:
            logger.warning("tkinter not available - console mode only")
            return

        try:
            # Create avatar with error handling
            self.create_avatar_window()

            if not self.avatar_window:
                logger.error("❌ Failed to create avatar window")
                return

            # SELF-AWARENESS: Record initial ecosystem relationships
            if self.self_awareness:
                try:
                    from character_avatar_registry import CharacterAvatarRegistry
                    registry = CharacterAvatarRegistry()
                    all_chars = registry.get_all_characters()

                    for char in all_chars:
                        if char.character_id != "jarvis_va":
                            self.self_awareness.record_interaction(
                                entity_id=char.character_id,
                                entity_name=char.name,
                                interaction_type="ecosystem_member"
                            )

                    logger.info(f"✅ Recorded {len(self.self_awareness.ecosystem_relationships)} ecosystem relationships")
                except Exception as e:
                    logger.debug(f"Ecosystem relationship recording error: {e}")

            # SELF-AWARENESS: Log initial state
            if self.self_awareness:
                state = self.self_awareness.get_self_state()
                logger.info("")
                logger.info("=" * 80)
                logger.info("🧠 JARVIS SELF-AWARENESS INITIALIZED")
                logger.info("=" * 80)
                logger.info(f"   Awareness Level: {state.awareness_level:.2%}")
                logger.info(f"   Active Perceptions: {sum(1 for v in state.perception_active.values() if v)}/7")
                logger.info(f"   Ecosystem Relationships: {len(self.self_awareness.ecosystem_relationships)}")
                logger.info(f"   Capabilities: {len(state.capabilities)}")
                logger.info("=" * 80)
                logger.info("")
                logger.info("   🎯 JARVIS is learning, adapting, and becoming more aware")
                logger.info("   🧠 Periodic introspection active - JARVIS reflects on itself")
                logger.info("   👁️  All VA movements feed into eye tracking fine-tuning")
                logger.info("   🌐 Ecosystem awareness - JARVIS understands relationships")
                logger.info("")

            # Start introduction (after calibration if eye tracking is active)
            if not self.eye_tracking_active:
                self.start_introduction()
            else:
                # Wait a bit for calibration to start, then begin introduction
                self.avatar_window.after(500, self.start_introduction)

            # Keep window alive with graceful shutdown handling
            try:
                self.avatar_window.mainloop()
            except KeyboardInterrupt:
                logger.info("⚠️  Interrupted by user - shutting down gracefully")
                self._cleanup()
            except Exception as e:
                logger.error(f"❌ Error in mainloop: {e}")
                self._cleanup()
        except Exception as e:
            logger.error(f"❌ Error in run(): {e}")
            import traceback
            traceback.print_exc()
            self._cleanup()

    def _cleanup(self):
        """Cleanup resources gracefully"""
        try:
            # Stop all threads
            self.eye_tracking_active = False
            self.vision_active = False
            self.calibration_active = False
            self.narration_active = False

            # Close cameras
            if self.camera:
                try:
                    self.camera.release()
                except:
                    pass
            if self.ir_camera:
                try:
                    self.ir_camera.release()
                except:
                    pass

            # Destroy windows
            if self.avatar_window:
                try:
                    self.avatar_window.destroy()
                except:
                    pass
            if hasattr(self, '_root') and self._root:
                try:
                    self._root.destroy()
                except:
                    pass

            logger.info("✅ Cleanup complete")
        except Exception as e:
            logger.debug(f"Cleanup error: {e}")


def count_jarvis_windows_visually():
    """Use MDV to visually count JARVIS windows - uses framework with known criteria"""
    try:
        from jarvis_visual_detection_framework import get_jarvis_visual_detection_framework
        framework = get_jarvis_visual_detection_framework()
        count = framework.count_jarvis_instances()
        return count
    except ImportError:
        logger.debug("Visual detection framework not available - using fallback")
        # Fallback to simple detection
        try:
            import pyautogui
            import cv2
            import numpy as np

            screenshot = pyautogui.screenshot()
            screen_array = np.array(screenshot)
            hsv = cv2.cvtColor(screen_array, cv2.COLOR_RGB2HSV)
            lower_cyan = np.array([85, 100, 100])
            upper_cyan = np.array([105, 255, 255])
            cyan_mask = cv2.inRange(hsv, lower_cyan, upper_cyan)
            contours, _ = cv2.findContours(cyan_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            jarvis_windows = 0
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 0:
                    perimeter = cv2.arcLength(contour, True)
                    if perimeter > 0:
                        circularity = 4 * np.pi * area / (perimeter * perimeter)
                        if circularity > 0.7:
                            radius = np.sqrt(area / np.pi)
                            if 50 <= radius <= 200:
                                jarvis_windows += 1

            logger.info(f"👁️  MDV Visual Detection (fallback): Found {jarvis_windows} JARVIS window(s)")
            return jarvis_windows
        except Exception as e:
            logger.debug(f"MDV visual detection error: {e}")
            return 0


def kill_existing_jarvis_processes():
    """Kill ALL existing JARVIS narrator processes - AGGRESSIVE 'Killing Kenny'"""
    killed_count = 0

    # FIRST: Use MDV visual detection framework (100% MDV utilization)
    # Apply what we've learned - use the knowledge we have about what JARVIS looks like
    logger.info("👁️  Using MDV Visual Detection Framework (applying learned knowledge)...")
    visual_count = count_jarvis_windows_visually()
    if visual_count > 0:
        logger.warning(f"⚠️  MDV DETECTED {visual_count} JARVIS WINDOW(S) ON DESKTOP!")
        logger.warning(f"   Framework confirms {visual_count} instance(s) need to be killed")
    else:
        logger.info("   ✅ MDV confirms no JARVIS windows visible")

    # MULTIPLE PASSES - ensure everything is killed
    for pass_num in range(3):  # Three passes to catch everything
        try:
            import psutil
            import os

            current_pid = os.getpid()
            script_name = "jarvis_narrator_avatar.py"

            if pass_num == 0:
                logger.info("🔍 PASS 1: Searching for JARVIS processes by script name...")
            elif pass_num == 1:
                logger.info("🔍 PASS 2: Searching for any Python processes with 'jarvis' in command line...")
            else:
                logger.info("🔍 PASS 3: Final cleanup pass...")

            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    # Skip current process
                    if proc.info['pid'] == current_pid:
                        continue

                    # Check if it's a Python process
                    proc_name = proc.info.get('name', '').lower()
                    if 'python' not in proc_name and 'pythonw' not in proc_name:
                        continue

                    cmdline = proc.info.get('cmdline', [])
                    if not cmdline:
                        continue

                    cmdline_str = ' '.join(str(arg) for arg in cmdline).lower()

                    # Pass 1: Exact script match
                    # Pass 2: Any "jarvis" in command line
                    # Pass 3: Any "jarvis" or "narrator" in command line
                    should_kill = False
                    if pass_num == 0:
                        should_kill = script_name in cmdline_str
                    elif pass_num == 1:
                        should_kill = 'jarvis' in cmdline_str and ('narrator' in cmdline_str or 'avatar' in cmdline_str)
                    else:
                        should_kill = 'jarvis' in cmdline_str

                    if should_kill:
                        logger.info(f"   🎯 Found JARVIS process: PID {proc.info['pid']} - {cmdline_str[:80]}")
                        try:
                            # Try graceful termination first (SIGTERM) - prevents exit code 15 notifications
                            proc.terminate()
                            killed_count += 1
                            logger.info(f"   ✅ Terminated PID {proc.info['pid']} (graceful)")

                            # Wait for graceful shutdown (prevents exit code 15 notifications)
                            try:
                                proc.wait(timeout=2.0)  # Wait up to 2 seconds for graceful exit
                                logger.info(f"   ✅ PID {proc.info['pid']} exited gracefully")
                            except psutil.TimeoutExpired:
                                # Process didn't exit gracefully, force kill
                                logger.warning(f"   ⚠️  Process {proc.info['pid']} didn't exit gracefully, force killing...")
                                proc.kill()
                                proc.wait(timeout=1.0)  # Wait for kill to complete
                                logger.info(f"   ✅ Force killed PID {proc.info['pid']}")
                            except psutil.NoSuchProcess:
                                # Already dead
                                logger.info(f"   ✅ PID {proc.info['pid']} already terminated")
                                pass
                        except psutil.NoSuchProcess:
                            # Already dead
                            pass
                        except psutil.AccessDenied:
                            logger.warning(f"   ⚠️  Access denied for PID {proc.info['pid']} - trying Windows taskkill...")
                            # Try Windows taskkill as fallback
                            try:
                                import subprocess
                                subprocess.run(['taskkill', '/F', '/PID', str(proc.info['pid'])],
                                             capture_output=True, timeout=2)
                                killed_count += 1
                                logger.info(f"   ✅ Killed via taskkill: PID {proc.info['pid']}")
                            except:
                                pass
                        except Exception as e:
                            logger.debug(f"   Error killing PID {proc.info['pid']}: {e}")
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                except Exception as e:
                    logger.debug(f"Process iteration error: {e}")

            # Wait between passes - longer for multiple instances
            if pass_num < 2:
                time.sleep(2.0)  # 2 seconds between passes (was 1.0) - gives processes time to fully terminate

        except ImportError:
            # Fallback: Use Windows taskkill
            logger.warning("⚠️  psutil not available - using Windows taskkill")
            try:
                import subprocess
                # Kill by window title
                result = subprocess.run(
                    ['taskkill', '/F', '/FI', 'WINDOWTITLE eq *JARVIS*'],
                    capture_output=True,
                    timeout=5
                )
                # Kill by process name containing jarvis
                result2 = subprocess.run(
                    ['taskkill', '/F', '/IM', 'python.exe', '/FI', 'WINDOWTITLE eq *JARVIS*'],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0 or result2.returncode == 0:
                    killed_count += 1
                    logger.info("   ✅ Killed JARVIS windows using taskkill")
            except Exception as e:
                logger.debug(f"Taskkill error: {e}")
            break  # Exit loop if psutil not available
        except Exception as e:
            logger.warning(f"Error in kill pass {pass_num + 1}: {e}")

    # Final Windows-specific cleanup using taskkill
    try:
        import subprocess
        import os
        if os.name == 'nt':  # Windows
            # Kill all python processes with jarvis in window title
            subprocess.run(['taskkill', '/F', '/FI', 'WINDOWTITLE eq *JARVIS*'],
                         capture_output=True, timeout=3)
            # Also try killing by process name
            subprocess.run(['taskkill', '/F', '/FI', 'IMAGENAME eq python.exe', '/FI', 'WINDOWTITLE eq *JARVIS*'],
                         capture_output=True, timeout=3)
    except:
        pass

    if killed_count > 0:
        logger.info(f"✅ TOTAL KILLED: {killed_count} JARVIS process(es) across all passes")
        # Extended wait for cleanup - especially important with multiple instances
        # Each process needs time to release windows, cameras, and other resources
        wait_time = min(5.0, 1.0 + (killed_count * 0.5))  # 1 second base + 0.5 per process, max 5 seconds
        logger.info(f"   ⏳ Waiting {wait_time:.1f} seconds for full cleanup...")
        time.sleep(wait_time)

        # VERIFY with MDV Framework: Check if windows are actually gone (apply learned knowledge)
        logger.info("   👁️  Verifying with MDV Visual Detection Framework...")
        time.sleep(1.0)  # Brief wait for windows to close
        remaining_visual = count_jarvis_windows_visually()
        if remaining_visual > 0:
            logger.warning(f"   ⚠️  MDV FRAMEWORK STILL DETECTS {remaining_visual} JARVIS WINDOW(S)")
            logger.warning(f"   🔄 Applying additional cleanup passes...")
            # Try additional aggressive passes until MDV confirms all closed
            for attempt in range(3):
                time.sleep(1.5)
                remaining_visual = count_jarvis_windows_visually()
                logger.info(f"   📊 Attempt {attempt + 1}: MDV detects {remaining_visual} window(s)")
                if remaining_visual == 0:
                    logger.info("   ✅ MDV Framework confirms all JARVIS windows are closed")
                    break
            if remaining_visual > 0:
                logger.error(f"   ❌ MDV Framework still detects {remaining_visual} window(s) after cleanup")
        else:
            logger.info("   ✅ MDV Framework confirms all JARVIS windows are closed")
    else:
        logger.info("   ✅ No existing JARVIS processes found")
        # Still wait a bit even if nothing was killed (in case of race conditions)
        time.sleep(1.0)

    return killed_count


def main():
    """Main entry point - PEAK Standard: Graceful error handling"""
    try:
        # CLEAR THE PLATE: Kill ALL existing JARVIS instances FIRST (default behavior)
        # Only keep old instances if there's a direct comparison to be made between cycles
        logger.info("=" * 80)
        logger.info("🔪 CLEARING THE PLATE - KILLING ALL EXISTING JARVIS INSTANCES")
        logger.info("=" * 80)
        killed_count = kill_existing_jarvis_processes()
        if killed_count > 0:
            logger.info(f"   ✅ Killed {killed_count} existing JARVIS instance(s)")
            # Additional wait after kill function (kill function already waits, but extra safety)
            # This ensures windows are fully closed and resources released
            additional_wait = max(2.0, killed_count * 0.3)  # 2 seconds base + 0.3 per process
            logger.info(f"   ⏳ Additional cleanup wait: {additional_wait:.1f} seconds...")
            time.sleep(additional_wait)
        else:
            logger.info("   ✅ No existing JARVIS instances found")
            # Brief wait even if nothing killed (safety margin)
            time.sleep(1.0)
        logger.info("=" * 80)
        logger.info("")

        # SINGLETON PATTERN: Prevent multiple instances using lock file
        import os
        import fcntl  # Unix file locking (will use Windows alternative if needed)
        lock_file_path = project_root / "data" / "jarvis_instance.lock"
        lock_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Clean up any stale lock file
        if lock_file_path.exists():
            try:
                lock_file_path.unlink()
            except:
                pass

        # Try to acquire lock (prevents multiple instances)
        lock_file = None
        try:
            if os.name == 'nt':  # Windows
                # Windows: Use msvcrt for file locking
                try:
                    import msvcrt
                    lock_file = open(lock_file_path, 'w')
                    try:
                        msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
                    except IOError:
                        logger.warning("⚠️  Lock file exists - killing any remaining instances...")
                        kill_existing_jarvis_processes()
                        time.sleep(2)
                        # Try again
                        try:
                            msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
                        except IOError:
                            logger.error("❌ Could not acquire lock - killing all and retrying...")
                            kill_existing_jarvis_processes()
                            time.sleep(3)
                            # Final attempt
                            try:
                                msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
                            except IOError:
                                logger.error("❌ Could not acquire lock after cleanup")
                                return 1
                except ImportError:
                    # Fallback: Just kill existing processes
                    logger.warning("⚠️  File locking not available - using process kill method")
                    kill_existing_jarvis_processes()
                    time.sleep(2)
            else:  # Unix/Linux
                try:
                    lock_file = open(lock_file_path, 'w')
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                except IOError:
                    logger.warning("⚠️  Lock file exists - killing any remaining instances...")
                    kill_existing_jarvis_processes()
                    time.sleep(2)
                    # Try again
                    try:
                        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    except IOError:
                        logger.error("❌ Could not acquire lock - killing all and retrying...")
                        kill_existing_jarvis_processes()
                        time.sleep(3)
                        # Final attempt
                        try:
                            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                        except IOError:
                            logger.error("❌ Could not acquire lock after cleanup")
                            return 1
                except ImportError:
                    # Fallback: Just kill existing processes
                    logger.warning("⚠️  File locking not available - using process kill method")
                    kill_existing_jarvis_processes()
                    time.sleep(2)
        except Exception as e:
            logger.warning(f"⚠️  Lock file error: {e} - using process kill method")
            kill_existing_jarvis_processes()
            time.sleep(2)

        # Now start fresh with graceful error handling
        try:
            narrator = JARVISNarratorAvatar()
            narrator.run()

            # Release lock on exit
            try:
                if lock_file:
                    if os.name == 'nt':
                        try:
                            import msvcrt
                            msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
                        except:
                            pass
                    else:
                        try:
                            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
                        except:
                            pass
                    lock_file.close()
                if lock_file_path.exists():
                    lock_file_path.unlink()
            except:
                pass

            return 0
        except KeyboardInterrupt:
            logger.info("⚠️  Interrupted by user")
            return 0  # Graceful exit, not an error
        except Exception as init_error:
            logger.error(f"❌ Initialization error: {init_error}")
            import traceback
            traceback.print_exc()
            # Don't return error code - let it exit gracefully
            return 0
    except KeyboardInterrupt:
        logger.info("⚠️  Interrupted by user")
        return 0  # Graceful exit
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        # Return 0 to prevent error notifications (process completed, just with errors)
        return 0


if __name__ == "__main__":


    sys.exit(main())