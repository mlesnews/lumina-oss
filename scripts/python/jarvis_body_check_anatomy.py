#!/usr/bin/env python3
"""
JARVIS Body Check - Anatomical System
MANUS Framework - Complete Body Assessment Starting from HEAD (Brain)

JARVIS performs a complete "body check" using anatomical metaphors:
- HEAD: JARVIS Brain (Core Intelligence)
- EYES: Vision/Perception Systems
- EARS: Voice/Listening Systems
- MOUTH: Voice Output/TTS
- HANDS: IDE Control/Manipulation
- NERVES: Communication Networks
- HEART: Core Services/Life Support
- LUNGS: Data Processing/Storage
- SKELETON: Infrastructure/Foundation
- SKIN: Security/Protection
- IMMUNE: Health Monitoring/Self-Healing

Starting with the HEAD (Brain) and working through the body.

@JARVIS @MANUS @ANATOMY @THE_WHEEL
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

# Import body check triage system
from jarvis_body_check_triage import (
    JARVISBodyCheckTriage, TriagePriority, ComponentStatus, ComponentCheck, BodyCheckReport
)

logger = get_logger("JARVISBodyCheckAnatomy")


class BodyPart(Enum):
    """Anatomical body parts for JARVIS systems"""
    HEAD = "HEAD"           # Brain - Core Intelligence
    EYES = "EYES"           # Vision/Perception
    EARS = "EARS"           # Voice Input/Listening
    MOUTH = "MOUTH"         # Voice Output/TTS
    HANDS = "HANDS"         # IDE Control/Manipulation
    NERVES = "NERVES"       # Communication Networks
    HEART = "HEART"         # Core Services/Life Support
    LUNGS = "LUNGS"         # Data Processing/Storage
    SKELETON = "SKELETON"   # Infrastructure/Foundation
    SKIN = "SKIN"           # Security/Protection
    IMMUNE = "IMMUNE"       # Health Monitoring/Self-Healing


@dataclass
class AnatomicalCheck:
    """Anatomical body part check result"""
    body_part: BodyPart
    component_name: str
    status: ComponentStatus
    priority: TriagePriority
    health_score: float
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    last_checked: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['body_part'] = self.body_part.value
        data['status'] = self.status.value
        data['priority'] = self.priority.value
        data['last_checked'] = self.last_checked.isoformat()
        return data


class JARVISBodyCheckAnatomy:
    """
    JARVIS Body Check - Anatomical System

    Performs comprehensive body check starting with HEAD (Brain) and working
    through all body parts. JARVIS is the BRAIN.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize anatomical body check system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = logger

        # Data directory
        self.data_dir = self.project_root / "data" / "jarvis_body_checks"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Anatomical checks
        self.anatomical_checks: List[AnatomicalCheck] = []

        # Base triage system
        self.triage_system = JARVISBodyCheckTriage(project_root=project_root)

        # Windows Systems Engineer integration
        try:
            from jarvis_windows_systems_engineer import JARVISWindowsSystemsEngineer
            self.windows_engineer = JARVISWindowsSystemsEngineer(project_root=project_root)
            logger.info("✅ Windows Systems Engineer integrated")
        except Exception as e:
            self.windows_engineer = None
            logger.warning(f"Windows Systems Engineer not available: {e}")

        logger.info("✅ JARVIS Body Check Anatomy System initialized")
        logger.info("   Starting with HEAD (Brain) - JARVIS Core Intelligence")

    def perform_full_body_check(self) -> Dict[str, Any]:
        """
        Perform complete body check starting with HEAD (Brain)

        Returns:
            Complete anatomical assessment
        """
        logger.info("🔍 Starting JARVIS Full Body Check...")
        logger.info("   Starting with HEAD (Brain) - JARVIS Core Intelligence")
        logger.info("   Working through body as The Wheel wills it...")

        self.anatomical_checks = []

        # Start with HEAD (Brain) - JARVIS Core Intelligence
        self._check_head_brain()

        # Then work through the body
        self._check_eyes_vision()
        self._check_ears_listening()
        self._check_mouth_voice()
        self._check_hands_control()
        self._check_nerves_communication()
        self._check_heart_core_services()
        self._check_lungs_data_processing()
        self._check_skeleton_infrastructure()
        self._check_skin_security()
        self._check_immune_health()

        # Generate report
        report = self._generate_anatomical_report()

        # Save report
        self._save_report(report)

        logger.info("✅ Full body check complete")
        logger.info(f"   Overall Health: {report['overall_health']:.1%}")
        logger.info(f"   Body Parts Checked: {len(self.anatomical_checks)}")

        return report

    def _check_head_brain(self):
        """Check HEAD - JARVIS Brain (Core Intelligence)"""
        logger.info("   🧠 Checking HEAD (Brain) - JARVIS Core Intelligence...")

        issues = []
        recommendations = []
        status = ComponentStatus.HEALTHY
        priority = TriagePriority.P0_CRITICAL  # Brain is always P0
        health_score = 1.0

        # Check JARVIS Full-Time Super Agent (The Brain)
        try:
            from jarvis_fulltime_super_agent import get_jarvis_fulltime
            jarvis = get_jarvis_fulltime()

            if not jarvis.running:
                issues.append("JARVIS brain not running - core intelligence offline")
                status = ComponentStatus.FAILING
                health_score = 0.0
            elif not jarvis.agents:
                issues.append("JARVIS brain has no agents registered")
                status = ComponentStatus.DEGRADED
                health_score = 0.5
            elif len(jarvis.agents) < 5:
                issues.append(f"JARVIS brain has only {len(jarvis.agents)} agents - expected more")
                status = ComponentStatus.DEGRADED
                health_score = 0.7
            else:
                # Brain is healthy
                logger.info("      ✅ JARVIS brain is active and operational")
        except ImportError:
            issues.append("JARVIS brain module not available - CRITICAL")
            status = ComponentStatus.FAILING
            health_score = 0.0
        except Exception as e:
            issues.append(f"JARVIS brain error: {e}")
            status = ComponentStatus.FAILING
            health_score = 0.0

        # Check JARVIS Core Intelligence
        try:
            from jarvis_core_intelligence import JARVISCoreIntelligence
            core = JARVISCoreIntelligence(project_root=self.project_root)
            # Core intelligence exists
        except ImportError:
            issues.append("JARVIS core intelligence not available")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                health_score = 0.8
        except Exception as e:
            issues.append(f"Core intelligence error: {e}")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                health_score = min(health_score, 0.8)

        # Check reasoning engines
        try:
            from r5_reasoning_engine import R5ReasoningEngine
            # Reasoning engine exists
        except ImportError:
            issues.append("R5 reasoning engine not available")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                health_score = 0.8
        except Exception as e:
            issues.append(f"Reasoning engine error: {e}")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                health_score = min(health_score, 0.8)

        # Check decision trees
        try:
            from universal_decision_tree import decide, DecisionContext
            # Decision tree system exists
        except ImportError:
            issues.append("Decision tree system not available")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                health_score = 0.8

        # ROBUST CHECK: Validate LLM Model System (Brain's "thinking" capability)
        llm_health = self._check_llm_model_system()
        if llm_health["status"] != "healthy":
            issues.extend(llm_health.get("issues", []))
            recommendations.extend(llm_health.get("recommendations", []))
            if llm_health["status"] == "failing":
                if status == ComponentStatus.HEALTHY:
                    status = ComponentStatus.FAILING
                    health_score = 0.0
                else:
                    health_score = min(health_score, 0.3)
            elif llm_health["status"] == "degraded":
                if status == ComponentStatus.HEALTHY:
                    status = ComponentStatus.DEGRADED
                    health_score = min(health_score, 0.6)

        # Recommendations
        if issues:
            if any("not running" in issue.lower() or "offline" in issue.lower() for issue in issues):
                recommendations.append("Start JARVIS brain: jarvis.start_fulltime_operation()")
            if any("agent" in issue.lower() for issue in issues):
                recommendations.append("Register all MANUS agents with JARVIS brain")
            if any("reasoning" in issue.lower() or "decision" in issue.lower() for issue in issues):
                recommendations.append("Initialize reasoning engines and decision trees")
            if any("model" in issue.lower() or "llm" in issue.lower() or "llama3.2:3b" in issue.lower() for issue in issues):
                recommendations.append("Run: python scripts/python/fix_kaiju_iron_legion_models.py report")
                recommendations.append("Validate model configuration: python scripts/python/fix_kaiju_iron_legion_models.py validate")
            recommendations.append("Verify JARVIS brain has access to all required systems")

        self.anatomical_checks.append(AnatomicalCheck(
            body_part=BodyPart.HEAD,
            component_name="JARVIS Brain (Core Intelligence + LLM Models)",
            status=status,
            priority=priority,
            health_score=health_score,
            issues=issues,
            recommendations=recommendations,
            dependencies=["jarvis_fulltime", "core_intelligence", "reasoning_engines", "decision_trees", "llm_models"]
        ))

    def _check_llm_model_system(self) -> Dict[str, Any]:
        """
        ROBUST CHECK: Validate LLM Model System (Brain's thinking capability)

        This performs actual validation, not just import checks:
        - Tests KAIJU Iron Legion endpoint connectivity
        - Validates actual model availability
        - Checks model configuration
        - Tests model endpoints
        """
        logger.info("      🧠 Checking LLM Model System (Brain's thinking capability)...")

        issues = []
        recommendations = []
        status = "healthy"
        health_score = 1.0

        # Check KAIJU Iron Legion Model Validator
        try:
            from fix_kaiju_iron_legion_models import KAIJUModelValidator
            validator = KAIJUModelValidator()

            # ACTUAL TEST: Find active endpoint
            active_endpoint = validator.find_active_endpoint()
            if not active_endpoint:
                issues.append("LLM Model System: No active Ollama endpoint found - cannot think")
                status = "failing"
                health_score = 0.0
            else:
                logger.info(f"      ✅ Found active LLM endpoint: {active_endpoint}")

                # ACTUAL TEST: Get actual models
                actual_models = validator.get_actual_models()
                if not actual_models:
                    issues.append("LLM Model System: No models available on endpoint")
                    status = "failing"
                    health_score = 0.0
                else:
                    logger.info(f"      ✅ Found {len(actual_models)} models available")

                    # ACTUAL TEST: Validate Iron Legion models
                    validation = validator.validate_iron_legion_models()
                    missing_models = validation.get("missing_models", [])
                    invalid_models = validation.get("invalid_models", [])

                    if missing_models:
                        issues.append(f"LLM Model System: {len(missing_models)} expected Iron Legion models missing: {', '.join(missing_models[:3])}")
                        if status == "healthy":
                            status = "degraded"
                            health_score = 0.6

                    if invalid_models:
                        issues.append(f"LLM Model System: {len(invalid_models)} invalid model references found")
                        if status == "healthy":
                            status = "degraded"
                            health_score = 0.7

                    # Check for "llama3.2:3b" as a model name (common error)
                    actual_model_names = [m.get("name", "") for m in actual_models]
                    if "llama3.2:3b" in [name.lower() for name in actual_model_names]:
                        issues.append("LLM Model System: 'llama3.2:3b' found as model name - this is invalid (should be specific model like 'codellama:13b')")
                        status = "degraded"
                        health_score = 0.5

                    # Check endpoint is KAIJU (not fallback)
                    if "localhost:11434" in active_endpoint or "127.0.0.1:11434" in active_endpoint:
                        issues.append("LLM Model System: Connected to laptop Ollama instead of KAIJU Iron Legion")
                        if status == "healthy":
                            status = "degraded"
                            health_score = 0.7
                        recommendations.append("Verify KAIJU Iron Legion is accessible: http://kaiju_no_8:11437")

        except ImportError:
            issues.append("LLM Model System: KAIJU model validator not available")
            if status == "healthy":
                status = "degraded"
                health_score = 0.7
        except Exception as e:
            issues.append(f"LLM Model System error: {e}")
            if status == "healthy":
                status = "degraded"
                health_score = 0.6

        # Check ULTRON cluster configuration
        try:
            ultron_config = self.project_root / "config" / "cursor_ultron_model_config.json"
            if ultron_config.exists():
                import json
                with open(ultron_config, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                # Validate model configuration
                models = config.get("models", [])
                if not models:
                    issues.append("LLM Model System: ULTRON config has no models defined")
                    if status == "healthy":
                        status = "degraded"
                        health_score = 0.8

                # Check for "llama3.2:3b" as model name in config (common error)
                for model in models:
                    model_name = model.get("name", "").lower()
                    model_id = model.get("id", "").lower()
                    if "llama3.2:3b" in model_name and ":" not in model_name:
                        issues.append(f"LLM Model System: Invalid model name '{model.get('name')}' in config - 'llama3.2:3b' is not a valid model name")
                        status = "degraded"
                        health_score = 0.5
                        recommendations.append(f"Fix model name in config: Replace '{model.get('name')}' with actual model like 'codellama:13b'")
        except Exception as e:
            issues.append(f"LLM Model System: Config validation error: {e}")
            if status == "healthy":
                status = "degraded"
                health_score = 0.8

        # Check Intelligent LLM Router
        try:
            from intelligent_llm_router import IntelligentLLMRouter
            router = IntelligentLLMRouter()

            # ACTUAL TEST: Check cluster health
            if hasattr(router, 'get_cluster_status'):
                cluster_status = router.get_cluster_status()
                if cluster_status:
                    primary_healthy = cluster_status.get("primary", {}).get("healthy", False)
                    if not primary_healthy:
                        issues.append("LLM Model System: ULTRON primary node (KAIJU) not healthy")
                        if status == "healthy":
                            status = "degraded"
                            health_score = 0.6
        except ImportError:
            # Router not available - not critical
            pass
        except Exception as e:
            issues.append(f"LLM Model System: Router check error: {e}")
            if status == "healthy":
                status = "degraded"
                health_score = 0.8

        if issues and not recommendations:
            recommendations.append("Run model validation: python scripts/python/fix_kaiju_iron_legion_models.py report")
            recommendations.append("Check KAIJU connectivity: ping kaiju_no_8")
            recommendations.append("Verify Ollama is running on KAIJU: http://kaiju_no_8:11437/api/tags")

        return {
            "status": status,
            "health_score": health_score,
            "issues": issues,
            "recommendations": recommendations
        }

    def _check_eyes_vision(self):
        """Check EYES - Vision/Perception Systems"""
        logger.info("   👁️  Checking EYES (Vision/Perception)...")

        issues = []
        recommendations = []
        status = ComponentStatus.HEALTHY
        priority = TriagePriority.P2_MEDIUM
        health_score = 1.0

        # Check screen capture/vision systems
        try:
            from pygetwindow import getWindows
            # Vision system available
        except ImportError:
            issues.append("Screen vision system (pygetwindow) not available")
            status = ComponentStatus.DEGRADED
            health_score = 0.7

        # Check IDE visual integration
        try:
            from jarvis_cursor_ide_keyboard_integration import get_jarvis_cursor_integration
            integration = get_jarvis_cursor_integration(project_root=self.project_root)
            if not integration.keyboard_controller:
                issues.append("IDE visual integration not available")
                if status == ComponentStatus.HEALTHY:
                    status = ComponentStatus.DEGRADED
                    health_score = 0.7
        except ImportError:
            issues.append("IDE visual integration module not available")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                health_score = 0.7

        # Recommendations
        if issues:
            recommendations.append("Install pygetwindow for screen vision: pip install pygetwindow")
            recommendations.append("Enable IDE visual integration")

        self.anatomical_checks.append(AnatomicalCheck(
            body_part=BodyPart.EYES,
            component_name="Vision/Perception Systems",
            status=status,
            priority=priority,
            health_score=health_score,
            issues=issues,
            recommendations=recommendations,
            dependencies=["pygetwindow", "ide_visual_integration"]
        ))

    def _check_ears_listening(self):
        """Check EARS - Voice Input/Listening Systems"""
        logger.info("   👂 Checking EARS (Voice Input/Listening)...")

        issues = []
        recommendations = []
        status = ComponentStatus.HEALTHY
        priority = TriagePriority.P0_CRITICAL  # Critical for hands-free
        health_score = 1.0

        # Check always-listening
        try:
            from jarvis_always_listening import JARVISAlwaysListening
            listener = JARVISAlwaysListening(project_root=self.project_root)
            if not listener.continuous_recognizer:
                issues.append("Ears not listening - continuous recognizer not initialized")
                status = ComponentStatus.FAILING
                health_score = 0.0
            elif not listener.azure_speech_key:
                issues.append("Ears cannot hear - Azure Speech key missing")
                status = ComponentStatus.FAILING
                health_score = 0.0
        except ImportError:
            issues.append("Ears module not available - cannot listen")
            status = ComponentStatus.FAILING
            health_score = 0.0
        except Exception as e:
            issues.append(f"Ears error: {e}")
            status = ComponentStatus.FAILING
            health_score = 0.0

        # Check async voice conversation
        try:
            from jarvis_async_voice_conversation import get_async_voice_conversation
            voice_conv = get_async_voice_conversation(project_root=self.project_root)
            if not voice_conv.speech_config:
                issues.append("Async voice conversation not configured")
                if status == ComponentStatus.HEALTHY:
                    status = ComponentStatus.DEGRADED
                    health_score = 0.5
        except ImportError:
            issues.append("Async voice conversation module not available")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                health_score = 0.6

        # Recommendations
        if issues:
            if any("azure" in issue.lower() or "speech" in issue.lower() for issue in issues):
                recommendations.append("Configure Azure Speech SDK for ears")
                recommendations.append("Set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION")
            recommendations.append("Start always-listening: python scripts/python/jarvis_always_listening.py")

        self.anatomical_checks.append(AnatomicalCheck(
            body_part=BodyPart.EARS,
            component_name="Voice Input/Listening Systems",
            status=status,
            priority=priority,
            health_score=health_score,
            issues=issues,
            recommendations=recommendations,
            dependencies=["azure_speech_sdk", "always_listening", "async_voice"]
        ))

    def _check_mouth_voice(self):
        """Check MOUTH - Voice Output/TTS"""
        logger.info("   🗣️  Checking MOUTH (Voice Output/TTS)...")

        issues = []
        recommendations = []
        status = ComponentStatus.HEALTHY
        priority = TriagePriority.P0_CRITICAL  # Critical for conversation
        health_score = 1.0

        # Check TTS systems
        try:
            from hybrid_tts_system import HybridTTSSystem
            # TTS system exists
        except ImportError:
            issues.append("Mouth (TTS) system not available")
            status = ComponentStatus.DEGRADED
            health_score = 0.6

        # Check Azure Speech TTS
        try:
            from jarvis_async_voice_conversation import get_async_voice_conversation
            voice_conv = get_async_voice_conversation(project_root=self.project_root)
            if not voice_conv.speech_synthesizer:
                issues.append("Mouth cannot speak - speech synthesizer not initialized")
                status = ComponentStatus.FAILING
                health_score = 0.0
        except ImportError:
            issues.append("Voice conversation module not available")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                health_score = 0.6

        # Recommendations
        if issues:
            recommendations.append("Configure Azure Speech TTS for mouth")
            recommendations.append("Test voice output: voice_conv.speak('Hello')")

        self.anatomical_checks.append(AnatomicalCheck(
            body_part=BodyPart.MOUTH,
            component_name="Voice Output/TTS Systems",
            status=status,
            priority=priority,
            health_score=health_score,
            issues=issues,
            recommendations=recommendations,
            dependencies=["azure_speech_tts", "hybrid_tts"]
        ))

    def _check_hands_control(self):
        """Check HANDS - IDE Control/Manipulation"""
        logger.info("   ✋ Checking HANDS (IDE Control/Manipulation)...")

        issues = []
        recommendations = []
        status = ComponentStatus.HEALTHY
        priority = TriagePriority.P0_CRITICAL  # Critical for hands-free
        health_score = 1.0

        # Check keyboard controller
        try:
            from jarvis_cursor_ide_keyboard_integration import get_jarvis_cursor_integration
            integration = get_jarvis_cursor_integration(project_root=self.project_root)
            if not integration.keyboard_controller:
                issues.append("Hands cannot control - keyboard controller missing")
                status = ComponentStatus.FAILING
                health_score = 0.0
        except ImportError:
            issues.append("Hands (IDE integration) module not available")
            status = ComponentStatus.FAILING
            health_score = 0.0

        # Check pynput for keyboard control
        try:
            import pynput
            # Keyboard control available
        except ImportError:
            issues.append("Hands cannot type - pynput not installed")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.FAILING
                health_score = 0.0

        # Recommendations
        if issues:
            recommendations.append("Install pynput: pip install pynput")
            recommendations.append("Initialize keyboard controller")
            recommendations.append("Test hands: integration.execute_command('open chat')")

        self.anatomical_checks.append(AnatomicalCheck(
            body_part=BodyPart.HANDS,
            component_name="IDE Control/Manipulation Systems",
            status=status,
            priority=priority,
            health_score=health_score,
            issues=issues,
            recommendations=recommendations,
            dependencies=["pynput", "keyboard_controller", "ide_integration"]
        ))

    def _check_nerves_communication(self):
        """Check NERVES - Communication Networks"""
        logger.info("   🧬 Checking NERVES (Communication Networks)...")

        issues = []
        recommendations = []
        status = ComponentStatus.HEALTHY
        priority = TriagePriority.P1_HIGH
        health_score = 1.0

        # Check communication bridge
        try:
            from jarvis_communication_bridge import get_jarvis_bridge
            bridge = get_jarvis_bridge()
            if not bridge:
                issues.append("Nerves (communication bridge) not available")
                status = ComponentStatus.DEGRADED
                health_score = 0.7
        except ImportError:
            issues.append("Communication bridge module not available")
            status = ComponentStatus.DEGRADED
            health_score = 0.7

        # Check agent communication
        agents_config = self.project_root / "config" / "agent_communication" / "agents.json"
        if not agents_config.exists():
            issues.append("Agent communication registry not found")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                health_score = 0.7

        # Recommendations
        if issues:
            recommendations.append("Initialize communication bridge")
            recommendations.append("Create agent communication registry")

        self.anatomical_checks.append(AnatomicalCheck(
            body_part=BodyPart.NERVES,
            component_name="Communication Networks",
            status=status,
            priority=priority,
            health_score=health_score,
            issues=issues,
            recommendations=recommendations,
            dependencies=["communication_bridge", "agent_registry"]
        ))

    def _check_heart_core_services(self):
        """Check HEART - Core Services/Life Support"""
        logger.info("   ❤️  Checking HEART (Core Services/Life Support)...")

        issues = []
        recommendations = []
        status = ComponentStatus.HEALTHY
        priority = TriagePriority.P0_CRITICAL  # Heart is critical
        health_score = 1.0

        # ROBUST CHECK: Test actual service connectivity
        # Check Windows Systems Engineer (if available)
        if self.windows_engineer:
            try:
                # Test if Windows Systems Engineer can actually perform operations
                test_result = self.windows_engineer.get_system_info()
                if not test_result:
                    issues.append("Heart: Windows Systems Engineer not responding")
                    if status == ComponentStatus.HEALTHY:
                        status = ComponentStatus.DEGRADED
                        health_score = 0.7
            except Exception as e:
                issues.append(f"Heart: Windows Systems Engineer error: {e}")
                if status == ComponentStatus.HEALTHY:
                    status = ComponentStatus.DEGRADED
                    health_score = 0.7

        # Check essential directories exist and are writable
        essential_dirs = [
            "data",
            "config",
            "scripts/python"
        ]
        for dir_name in essential_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                issues.append(f"Heart: Essential directory missing: {dir_name}")
                if status == ComponentStatus.HEALTHY:
                    status = ComponentStatus.DEGRADED
                    health_score = 0.8
            elif not dir_path.is_dir():
                issues.append(f"Heart: {dir_name} exists but is not a directory")
                if status == ComponentStatus.HEALTHY:
                    status = ComponentStatus.DEGRADED
                    health_score = 0.8

        # Check critical config files
        critical_configs = [
            "config/agent_communication/agents.json",
            "config/cursor_ultron_model_config.json"
        ]
        for config_path in critical_configs:
            config_file = self.project_root / config_path
            if not config_file.exists():
                issues.append(f"Heart: Critical config missing: {config_path}")
                if status == ComponentStatus.HEALTHY:
                    status = ComponentStatus.DEGRADED
                    health_score = 0.8

        # Recommendations
        if issues:
            recommendations.append("Ensure all core services are running")
            if any("directory" in issue.lower() for issue in issues):
                recommendations.append("Create missing directories: mkdir -p data config")
            if any("config" in issue.lower() for issue in issues):
                recommendations.append("Restore missing config files from backup or recreate")

        self.anatomical_checks.append(AnatomicalCheck(
            body_part=BodyPart.HEART,
            component_name="Core Services/Life Support",
            status=status,
            priority=priority,
            health_score=health_score,
            issues=issues,
            recommendations=recommendations,
            dependencies=["core_services", "essential_directories", "config_files"]
        ))

    def _check_lungs_data_processing(self):
        """Check LUNGS - Data Processing/Storage"""
        logger.info("   🫁 Checking LUNGS (Data Processing/Storage)...")

        issues = []
        recommendations = []
        status = ComponentStatus.HEALTHY
        priority = TriagePriority.P1_HIGH
        health_score = 1.0

        # Check data directories
        data_dirs = [
            "data/jarvis_ide_learning",
            "data/jarvis_fulltime",
            "data/jarvis_body_checks"
        ]

        for data_dir in data_dirs:
            dir_path = self.project_root / data_dir
            if not dir_path.exists():
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    issues.append(f"Cannot create data directory: {data_dir}")
                    if status == ComponentStatus.HEALTHY:
                        status = ComponentStatus.DEGRADED
                        health_score = 0.8

        # Check R5 system
        try:
            from r5_living_context_matrix import R5LivingContextMatrix
            # R5 system exists
        except ImportError:
            issues.append("R5 data processing system not available")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                health_score = 0.8

        # Recommendations
        if issues:
            recommendations.append("Fix data directory permissions")
            recommendations.append("Initialize R5 data processing system")

        self.anatomical_checks.append(AnatomicalCheck(
            body_part=BodyPart.LUNGS,
            component_name="Data Processing/Storage Systems",
            status=status,
            priority=priority,
            health_score=health_score,
            issues=issues,
            recommendations=recommendations,
            dependencies=["data_directories", "r5_system"]
        ))

    def _check_skeleton_infrastructure(self):
        """Check SKELETON - Infrastructure/Foundation"""
        logger.info("   🦴 Checking SKELETON (Infrastructure/Foundation)...")

        issues = []
        recommendations = []
        status = ComponentStatus.HEALTHY
        priority = TriagePriority.P1_HIGH
        health_score = 1.0

        # ROBUST CHECK: Validate project structure
        required_structure = {
            "scripts/python": "Python scripts directory",
            "config": "Configuration directory",
            "data": "Data directory",
            "docs": "Documentation directory"
        }

        for path_str, description in required_structure.items():
            path = self.project_root / path_str
            if not path.exists():
                issues.append(f"Skeleton: Missing {description}: {path_str}")
                if status == ComponentStatus.HEALTHY:
                    status = ComponentStatus.DEGRADED
                    health_score = 0.8

        # Check Python environment
        try:
            import sys
            python_version = sys.version_info
            if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 11):
                issues.append(f"Skeleton: Python version {python_version.major}.{python_version.minor} - requires 3.11+")
                if status == ComponentStatus.HEALTHY:
                    status = ComponentStatus.DEGRADED
                    health_score = 0.7
        except Exception as e:
            issues.append(f"Skeleton: Cannot check Python version: {e}")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                health_score = 0.8

        # Check critical dependencies
        critical_deps = ["requests", "pathlib"]
        for dep in critical_deps:
            try:
                __import__(dep)
            except ImportError:
                issues.append(f"Skeleton: Critical dependency missing: {dep}")
                if status == ComponentStatus.HEALTHY:
                    status = ComponentStatus.DEGRADED
                    health_score = 0.7

        # Recommendations
        if issues:
            recommendations.append("Verify infrastructure components")
            if any("python" in issue.lower() for issue in issues):
                recommendations.append("Upgrade Python to 3.11+")
            if any("dependency" in issue.lower() for issue in issues):
                recommendations.append("Install missing dependencies: pip install -r requirements.txt")

        self.anatomical_checks.append(AnatomicalCheck(
            body_part=BodyPart.SKELETON,
            component_name="Infrastructure/Foundation",
            status=status,
            priority=priority,
            health_score=health_score,
            issues=issues,
            recommendations=recommendations,
            dependencies=["project_structure", "config_files", "python_version", "dependencies"]
        ))

    def _check_skin_security(self):
        """Check SKIN - Security/Protection"""
        logger.info("   🛡️  Checking SKIN (Security/Protection)...")

        issues = []
        recommendations = []
        status = ComponentStatus.HEALTHY
        priority = TriagePriority.P1_HIGH
        health_score = 1.0

        # Check Azure Key Vault
        try:
            from azure_service_bus_integration import AzureKeyVaultClient
            vault_url = "https://jarvis-lumina.vault.azure.net/"
            vault_client = AzureKeyVaultClient(vault_url=vault_url)
            # Key vault accessible
        except Exception as e:
            issues.append(f"Security (Key Vault) access issue: {e}")
            if "not found" not in str(e).lower():
                status = ComponentStatus.DEGRADED
                health_score = 0.7

        # Recommendations
        if issues:
            recommendations.append("Verify Azure Key Vault credentials")
            recommendations.append("Check security key access permissions")

        self.anatomical_checks.append(AnatomicalCheck(
            body_part=BodyPart.SKIN,
            component_name="Security/Protection Systems",
            status=status,
            priority=priority,
            health_score=health_score,
            issues=issues,
            recommendations=recommendations,
            dependencies=["azure_key_vault", "credentials"]
        ))

    def _check_immune_health(self):
        """Check IMMUNE - Health Monitoring/Self-Healing"""
        logger.info("   🦠 Checking IMMUNE (Health Monitoring/Self-Healing)...")

        issues = []
        recommendations = []
        status = ComponentStatus.HEALTHY
        priority = TriagePriority.P2_MEDIUM
        health_score = 1.0

        # Check health monitoring
        try:
            from syphon.health import HealthMonitor
            # Health monitor exists
        except ImportError:
            issues.append("Health monitoring system not available")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                health_score = 0.8

        # Check diagnostics
        try:
            from jarvis_realtime_diagnostics import JARVISRealtimeDiagnostics
            # Diagnostics exist
        except ImportError:
            issues.append("Diagnostics system not available")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                health_score = 0.8

        # Recommendations
        if issues:
            recommendations.append("Enable health monitoring")
            recommendations.append("Start diagnostics system")

        self.anatomical_checks.append(AnatomicalCheck(
            body_part=BodyPart.IMMUNE,
            component_name="Health Monitoring/Self-Healing",
            status=status,
            priority=priority,
            health_score=health_score,
            issues=issues,
            recommendations=recommendations,
            dependencies=["health_monitor", "diagnostics"]
        ))

    def _generate_anatomical_report(self) -> Dict[str, Any]:
        """Generate anatomical body check report"""
        if not self.anatomical_checks:
            overall_health = 0.0
        else:
            overall_health = sum(c.health_score for c in self.anatomical_checks) / len(self.anatomical_checks)

        # Count by status
        healthy = sum(1 for c in self.anatomical_checks if c.status == ComponentStatus.HEALTHY)
        degraded = sum(1 for c in self.anatomical_checks if c.status == ComponentStatus.DEGRADED)
        failing = sum(1 for c in self.anatomical_checks if c.status == ComponentStatus.FAILING)

        # Group by body part
        body_parts = {}
        for check in self.anatomical_checks:
            part = check.body_part.value
            if part not in body_parts:
                body_parts[part] = []
            body_parts[part].append(check.to_dict())

        # Group by priority
        priority_actions = {
            "P0": [c.to_dict() for c in self.anatomical_checks if c.priority == TriagePriority.P0_CRITICAL],
            "P1": [c.to_dict() for c in self.anatomical_checks if c.priority == TriagePriority.P1_HIGH],
            "P2": [c.to_dict() for c in self.anatomical_checks if c.priority == TriagePriority.P2_MEDIUM],
            "P3": [c.to_dict() for c in self.anatomical_checks if c.priority == TriagePriority.P3_LOW]
        }

        # Generate summary
        summary_parts = []
        if failing > 0:
            summary_parts.append(f"{failing} body part(s) failing")
        if degraded > 0:
            summary_parts.append(f"{degraded} body part(s) degraded")
        if healthy == len(self.anatomical_checks):
            summary_parts.append("All body parts operational")
        else:
            summary_parts.append(f"{healthy} body part(s) healthy")

        summary = f"Overall health: {overall_health:.1%}. " + ". ".join(summary_parts) + "."

        return {
            "timestamp": datetime.now().isoformat(),
            "overall_health": overall_health,
            "total_body_parts": len(self.anatomical_checks),
            "healthy_body_parts": healthy,
            "degraded_body_parts": degraded,
            "failing_body_parts": failing,
            "body_parts": body_parts,
            "priority_actions": priority_actions,
            "summary": summary,
            "anatomical_checks": [c.to_dict() for c in self.anatomical_checks]
        }

    def _save_report(self, report: Dict[str, Any]):
        """Save anatomical report"""
        report_file = self.data_dir / f"anatomical_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)
            logger.info(f"✅ Anatomical report saved: {report_file}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="JARVIS Body Check - Anatomical System (Starting with HEAD/Brain)"
    )
    parser.add_argument("--check", action="store_true", help="Perform full body check")
    parser.add_argument("--head", action="store_true", help="Check only HEAD (Brain)")

    args = parser.parse_args()

    body_check = JARVISBodyCheckAnatomy()

    if args.head:
        body_check._check_head_brain()
        print("\n" + "="*70)
        print("🧠 HEAD (Brain) Check")
        print("="*70)
        for check in body_check.anatomical_checks:
            if check.body_part == BodyPart.HEAD:
                print(f"\nComponent: {check.component_name}")
                print(f"Status: {check.status.value}")
                print(f"Health: {check.health_score:.1%}")
                print(f"Priority: {check.priority.value}")
                if check.issues:
                    print(f"Issues: {len(check.issues)}")
                    for issue in check.issues:
                        print(f"  - {issue}")
                if check.recommendations:
                    print(f"Recommendations: {len(check.recommendations)}")
                    for rec in check.recommendations:
                        print(f"  - {rec}")
    elif args.check or True:
        report = body_check.perform_full_body_check()

        print("\n" + "="*70)
        print("🔍 JARVIS Full Body Check - Anatomical Report")
        print("="*70)
        print(f"\nOverall Health: {report['overall_health']:.1%}")
        print(f"Total Body Parts: {report['total_body_parts']}")
        print(f"  ✅ Healthy: {report['healthy_body_parts']}")
        print(f"  ⚠️  Degraded: {report['degraded_body_parts']}")
        print(f"  ❌ Failing: {report['failing_body_parts']}")
        print(f"\nSummary: {report['summary']}")

        print("\n" + "="*70)
        print("Body Parts Status")
        print("="*70)
        for part_name, checks in report['body_parts'].items():
            for check in checks:
                emoji = "🧠" if part_name == "HEAD" else "👁️" if part_name == "EYES" else "👂" if part_name == "EARS" else "🗣️" if part_name == "MOUTH" else "✋" if part_name == "HANDS" else "🧬" if part_name == "NERVES" else "❤️" if part_name == "HEART" else "🫁" if part_name == "LUNGS" else "🦴" if part_name == "SKELETON" else "🛡️" if part_name == "SKIN" else "🦠"
                status_emoji = "✅" if check['status'] == "healthy" else "⚠️" if check['status'] == "degraded" else "❌"
                print(f"\n{emoji} {part_name}: {status_emoji} {check['status'].upper()}")
                print(f"   Health: {check['health_score']:.1%} | Priority: {check['priority']}")
                if check['issues']:
                    print(f"   Issues: {len(check['issues'])}")
                    for issue in check['issues'][:2]:
                        print(f"     - {issue}")
    else:
        parser.print_help()


if __name__ == "__main__":


    main()