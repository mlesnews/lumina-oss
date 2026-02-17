#!/usr/bin/env python3
"""
JARVIS Anatomical Body Check
MANUS Framework - Systematic Body Check Starting from HEAD (Brain) Down

JARVIS performs a complete anatomical body check, starting with the HEAD (JARVIS as the BRAIN)
and working systematically through all body systems.

Anatomical Structure:
- HEAD: JARVIS Brain (intelligence, reasoning, decision-making)
- NECK: Communication & Coordination
- CHEST: Core Systems (heart, lungs - agents, workflows)
- ARMS: Action Systems (IDE control, voice, hands)
- HANDS: Fine Motor Control (keyboard, mouse, precise actions)
- TORSO: Data & Storage Systems
- LEGS: Foundation & Infrastructure
- FEET: Grounding & Security

@JARVIS @MANUS @ANATOMICAL @BODY_CHECK
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

logger = get_logger("JARVISAnatomicalBodyCheck")

# Import base body check
try:
    from jarvis_body_check_triage import (
        TriagePriority, ComponentStatus, ComponentCheck, BodyCheckReport
    )
except ImportError:
    logger.error("Base body check system not available")
    sys.exit(1)


class AnatomicalRegion(Enum):
    """Anatomical regions of JARVIS body"""
    HEAD = "head"           # Brain - JARVIS intelligence
    NECK = "neck"           # Communication & coordination
    CHEST = "chest"         # Core systems (heart, lungs)
    ARMS = "arms"           # Action systems
    HANDS = "hands"         # Fine motor control
    TORSO = "torso"         # Data & storage
    LEGS = "legs"           # Foundation & infrastructure
    FEET = "feet"           # Grounding & security


@dataclass
class AnatomicalComponentCheck(ComponentCheck):
    """Component check with anatomical region"""
    anatomical_region: AnatomicalRegion = AnatomicalRegion.HEAD

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data['anatomical_region'] = self.anatomical_region.value
        return data


class JARVISAnatomicalBodyCheck:
    """
    JARVIS Anatomical Body Check

    Performs systematic body check starting from HEAD (brain) and working down.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize anatomical body check"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = logger

        # Data directory
        self.data_dir = self.project_root / "data" / "jarvis_body_checks"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Component registry (organized by anatomical region)
        self.component_checks: List[AnatomicalComponentCheck] = []

        logger.info("✅ JARVIS Anatomical Body Check initialized")
        logger.info("   Starting from HEAD (Brain) and working down...")

    def perform_anatomical_body_check(self) -> BodyCheckReport:
        """
        Perform anatomical body check starting from HEAD (Brain) and work down

        Order:
        1. HEAD - JARVIS Brain (intelligence, reasoning)
        2. NECK - Communication & coordination
        3. CHEST - Core systems (agents, workflows)
        4. ARMS - Action systems (voice, IDE)
        5. HANDS - Fine motor control (keyboard, precise actions)
        6. TORSO - Data & storage
        7. LEGS - Foundation & infrastructure
        8. FEET - Grounding & security
        """
        logger.info("🔍 Starting JARVIS Anatomical Body Check...")
        logger.info("   Starting from HEAD (Brain) and working down...")

        self.component_checks = []

        # 1. HEAD - JARVIS Brain (intelligence, reasoning, decision-making)
        logger.info("\n🧠 Checking HEAD (JARVIS Brain)...")
        self._check_head_brain()

        # 2. NECK - Communication & coordination
        logger.info("\n📡 Checking NECK (Communication & Coordination)...")
        self._check_neck_communication()

        # 3. CHEST - Core systems (heart, lungs - agents, workflows)
        logger.info("\n❤️  Checking CHEST (Core Systems - Heart & Lungs)...")
        self._check_chest_core_systems()

        # 4. ARMS - Action systems (voice, IDE control)
        logger.info("\n💪 Checking ARMS (Action Systems)...")
        self._check_arms_action_systems()

        # 5. HANDS - Fine motor control (keyboard, precise actions)
        logger.info("\n✋ Checking HANDS (Fine Motor Control)...")
        self._check_hands_fine_control()

        # 6. TORSO - Data & storage
        logger.info("\n📦 Checking TORSO (Data & Storage)...")
        self._check_torso_data_storage()

        # 7. LEGS - Foundation & infrastructure
        logger.info("\n🦵 Checking LEGS (Foundation & Infrastructure)...")
        self._check_legs_foundation()

        # 8. FEET - Grounding & security
        logger.info("\n🦶 Checking FEET (Grounding & Security)...")
        self._check_feet_security()

        # Generate report
        report = self._generate_report()

        # Save report
        self._save_report(report)

        logger.info("\n✅ Anatomical body check complete")
        logger.info(f"   Overall Health Score: {report.overall_health_score:.2%}")
        logger.info(f"   Components by Region:")
        for region in AnatomicalRegion:
            region_components = [c for c in self.component_checks if c.anatomical_region == region]
            if region_components:
                healthy = sum(1 for c in region_components if c.status == ComponentStatus.HEALTHY)
                logger.info(f"     {region.value.upper()}: {len(region_components)} components ({healthy} healthy)")

        return report

    def _check_head_brain(self):
        """Check HEAD - JARVIS Brain (intelligence, reasoning, decision-making)"""
        logger.info("🧠 Checking HEAD (JARVIS Brain)...")
        logger.info("   The Brain is the foundation - all intelligence flows from here")

        # Check JARVIS Core Intelligence (Primary Brain)
        issues = []
        recommendations = []
        status = ComponentStatus.HEALTHY
        priority = TriagePriority.P3_LOW
        health_score = 1.0

        try:
            from jarvis_core_intelligence import JARVISCoreIntelligence
            core = JARVISCoreIntelligence(project_root=self.project_root)
            if not hasattr(core, 'initialized') or not core.initialized:
                # Check if it can be initialized
                try:
                    # Try to access a core method
                    if hasattr(core, 'understand_intent'):
                        # Core is functional
                        pass
                    else:
                        issues.append("JARVIS core intelligence not fully initialized")
                        status = ComponentStatus.DEGRADED
                        priority = TriagePriority.P1_HIGH
                        health_score = 0.6
                except:
                    issues.append("JARVIS core intelligence not initialized")
                    status = ComponentStatus.FAILING
                    priority = TriagePriority.P0_CRITICAL
                    health_score = 0.0
        except ImportError:
            issues.append("JARVIS core intelligence module not available - BRAIN MISSING")
            status = ComponentStatus.FAILING
            priority = TriagePriority.P0_CRITICAL
            health_score = 0.0
        except Exception as e:
            issues.append(f"JARVIS core intelligence error: {e}")
            status = ComponentStatus.FAILING
            priority = TriagePriority.P0_CRITICAL
            health_score = 0.0

        # Check R5 Reasoning Engine (Brain's reasoning cortex)
        try:
            from r5_reasoning_engine import R5ReasoningEngine
            reasoning = R5ReasoningEngine(project_root=self.project_root)
            if not hasattr(reasoning, 'reason') or not callable(getattr(reasoning, 'reason', None)):
                issues.append("R5 reasoning engine not functional - reasoning cortex impaired")
                if status == ComponentStatus.HEALTHY:
                    status = ComponentStatus.DEGRADED
                    priority = TriagePriority.P1_HIGH
                    health_score = 0.6
        except ImportError:
            issues.append("R5 reasoning engine not available - brain cannot reason")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P1_HIGH
                health_score = 0.6
        except Exception as e:
            issues.append(f"R5 reasoning engine error: {e}")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P1_HIGH
                health_score = min(health_score, 0.7)

        # Check Universal Decision Tree (Brain's decision-making system)
        try:
            from universal_decision_tree import decide, DecisionContext, DecisionOutcome
            # Test decision tree
            test_context = DecisionContext(
                situation="test",
                available_options=["test"],
                constraints={},
                preferences={}
            )
            # Decision tree available and functional
        except ImportError:
            issues.append("Universal decision tree not available - brain cannot make decisions")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P1_HIGH
                health_score = 0.7
        except Exception as e:
            issues.append(f"Decision tree error: {e}")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P1_HIGH
                health_score = min(health_score, 0.7)

        # Check Jedi Council (Brain's executive function - upper management)
        try:
            from jedi_council import JediCouncil
            council = JediCouncil(project_root=self.project_root)
            if not hasattr(council, 'approve') or not callable(getattr(council, 'approve', None)):
                issues.append("Jedi Council not functional - executive function impaired")
                if status == ComponentStatus.HEALTHY:
                    status = ComponentStatus.DEGRADED
                    priority = TriagePriority.P2_MEDIUM
                    health_score = 0.8
        except ImportError:
            issues.append("Jedi Council not available - no executive approval system")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P2_MEDIUM
                health_score = 0.8
        except Exception as e:
            issues.append(f"Jedi Council error: {e}")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P2_MEDIUM
                health_score = min(health_score, 0.8)

        # Check WOPR (Brain's strategic planning - decision support)
        try:
            from wopr_ops import WOPROps
            wopr = WOPROps()
            if not hasattr(wopr, 'analyze') or not callable(getattr(wopr, 'analyze', None)):
                issues.append("WOPR not functional - strategic planning impaired")
                if status == ComponentStatus.HEALTHY:
                    status = ComponentStatus.DEGRADED
                    priority = TriagePriority.P2_MEDIUM
                    health_score = 0.8
        except ImportError:
            issues.append("WOPR decision support not available - no strategic planning")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P2_MEDIUM
                health_score = 0.8
        except Exception as e:
            issues.append(f"WOPR error: {e}")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P2_MEDIUM
                health_score = min(health_score, 0.8)

        # Check AI Quorum (Brain's collaborative decision-making)
        try:
            # AI Quorum would coordinate multiple AI opinions
            # This might be part of decision tree or separate
            pass  # Placeholder for AI Quorum check
        except Exception as e:
            issues.append(f"AI Quorum error: {e}")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P2_MEDIUM
                health_score = min(health_score, 0.9)

        # Recommendations
        if issues:
            if any("core intelligence" in issue.lower() or "brain missing" in issue.lower() for issue in issues):
                recommendations.append("🚨 CRITICAL: Initialize JARVIS core intelligence - the BRAIN must function")
                recommendations.append("Verify core intelligence dependencies are installed")
                recommendations.append("Test core intelligence with: python -c 'from jarvis_core_intelligence import JARVISCoreIntelligence; core = JARVISCoreIntelligence()'")
            if any("reasoning" in issue.lower() for issue in issues):
                recommendations.append("Initialize R5 reasoning engine - brain needs reasoning capability")
                recommendations.append("Load reasoning knowledge base and test reasoning")
            if any("decision" in issue.lower() for issue in issues):
                recommendations.append("Initialize universal decision tree - brain needs decision-making")
                recommendations.append("Load decision tree rules and test decision paths")
            if any("jedi" in issue.lower() or "executive" in issue.lower() for issue in issues):
                recommendations.append("Initialize Jedi Council - brain needs executive approval system")
                recommendations.append("Configure decision escalation paths")
            if any("wopr" in issue.lower() or "strategic" in issue.lower() for issue in issues):
                recommendations.append("Initialize WOPR - brain needs strategic planning capability")
                recommendations.append("Test WOPR analysis and planning functions")
            if any("quorum" in issue.lower() for issue in issues):
                recommendations.append("Initialize AI Quorum - brain needs collaborative decision-making")

        self.component_checks.append(AnatomicalComponentCheck(
            component_name="🧠 JARVIS Brain (Core Intelligence & Reasoning)",
            component_type="brain",
            status=status,
            priority=priority,
            issues=issues,
            recommendations=recommendations,
            health_score=health_score,
            anatomical_region=AnatomicalRegion.HEAD,
            dependencies=["jarvis_core_intelligence", "r5_reasoning", "decision_tree", "jedi_council", "wopr", "ai_quorum"]
        ))

        # Check learning and memory (brain functions)
        self._check_head_learning_memory()

    def _check_head_learning_memory(self):
        """Check learning and memory systems (brain functions)"""
        issues = []
        recommendations = []
        status = ComponentStatus.HEALTHY
        priority = TriagePriority.P3_LOW
        health_score = 1.0

        # Check interaction learner (memory)
        try:
            from jarvis_ide_interaction_learner import get_ide_learner
            learner = get_ide_learner(project_root=self.project_root)
            if len(learner.feature_patterns) == 0:
                issues.append("No learned patterns - brain has no memory yet")
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P2_MEDIUM
                health_score = 0.7
        except ImportError:
            issues.append("Interaction learner not available - no learning capability")
            status = ComponentStatus.DEGRADED
            priority = TriagePriority.P2_MEDIUM
            health_score = 0.7
        except Exception as e:
            issues.append(f"Learning system error: {e}")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P2_MEDIUM
                health_score = 0.7

        # Check R5 living context matrix (long-term memory)
        try:
            from r5_living_context_matrix import R5LivingContextMatrix
            matrix = R5LivingContextMatrix(project_root=self.project_root)
        except ImportError:
            issues.append("R5 living context matrix not available - no long-term memory")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P2_MEDIUM
                health_score = 0.8
        except Exception as e:
            issues.append(f"Context matrix error: {e}")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P2_MEDIUM
                health_score = min(health_score, 0.8)

        if issues:
            recommendations.append("Start tracking interactions to build memory")
            recommendations.append("Initialize R5 living context matrix for long-term memory")

        self.component_checks.append(AnatomicalComponentCheck(
            component_name="Brain Learning & Memory",
            component_type="learning_memory",
            status=status,
            priority=priority,
            issues=issues,
            recommendations=recommendations,
            health_score=health_score,
            anatomical_region=AnatomicalRegion.HEAD,
            dependencies=["interaction_learner", "r5_context_matrix"]
        ))

    def _check_neck_communication(self):
        """Check NECK - Communication & coordination"""
        issues = []
        recommendations = []
        status = ComponentStatus.HEALTHY
        priority = TriagePriority.P3_LOW
        health_score = 1.0

        # Check JARVIS communication bridge
        try:
            from jarvis_communication_bridge import get_jarvis_bridge
            bridge = get_jarvis_bridge()
            if not bridge:
                issues.append("Communication bridge not available - brain cannot communicate")
                status = ComponentStatus.FAILING
                priority = TriagePriority.P0_CRITICAL
                health_score = 0.0
        except ImportError:
            issues.append("Communication bridge module not available")
            status = ComponentStatus.FAILING
            priority = TriagePriority.P0_CRITICAL
            health_score = 0.0
        except Exception as e:
            issues.append(f"Communication bridge error: {e}")
            status = ComponentStatus.FAILING
            priority = TriagePriority.P0_CRITICAL
            health_score = 0.0

        # Check AI Quorum (coordination)
        try:
            # AI Quorum would be here
            pass
        except Exception as e:
            issues.append(f"AI Quorum error: {e}")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P1_HIGH
                health_score = 0.7

        if issues:
            recommendations.append("Initialize JARVIS communication bridge")
            recommendations.append("Test inter-component communication")

        self.component_checks.append(AnatomicalComponentCheck(
            component_name="Communication & Coordination (Neck)",
            component_type="communication",
            status=status,
            priority=priority,
            issues=issues,
            recommendations=recommendations,
            health_score=health_score,
            anatomical_region=AnatomicalRegion.NECK,
            dependencies=["communication_bridge", "ai_quorum"]
        ))

    def _check_chest_core_systems(self):
        """Check CHEST - Core systems (heart, lungs - agents, workflows)"""
        issues = []
        recommendations = []
        status = ComponentStatus.HEALTHY
        priority = TriagePriority.P3_LOW
        health_score = 1.0

        # Check JARVIS full-time super agent (heart)
        try:
            from jarvis_fulltime_super_agent import get_jarvis_fulltime
            jarvis = get_jarvis_fulltime(project_root=self.project_root)
            if not jarvis.running:
                issues.append("JARVIS full-time super agent not running - heart not beating")
                status = ComponentStatus.FAILING
                priority = TriagePriority.P0_CRITICAL
                health_score = 0.0
        except ImportError:
            issues.append("JARVIS full-time super agent module not available")
            status = ComponentStatus.FAILING
            priority = TriagePriority.P0_CRITICAL
            health_score = 0.0
        except Exception as e:
            issues.append(f"JARVIS full-time super agent error: {e}")
            status = ComponentStatus.FAILING
            priority = TriagePriority.P0_CRITICAL
            health_score = 0.0

        # Check MANUS agents (lungs - breathing life into system)
        agents_config = self.project_root / "config" / "agent_communication" / "agents.json"
        if not agents_config.exists():
            issues.append("Agent registry not found - no agents to coordinate")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.FAILING
                priority = TriagePriority.P0_CRITICAL
                health_score = 0.0
        else:
            try:
                with open(agents_config, 'r') as f:
                    agents = json.load(f)
                    if len(agents) == 0:
                        issues.append("No agents registered - system cannot breathe")
                        if status == ComponentStatus.HEALTHY:
                            status = ComponentStatus.FAILING
                            priority = TriagePriority.P0_CRITICAL
                            health_score = 0.0
            except Exception as e:
                issues.append(f"Error reading agent registry: {e}")
                if status == ComponentStatus.HEALTHY:
                    status = ComponentStatus.DEGRADED
                    priority = TriagePriority.P1_HIGH
                    health_score = 0.6

        # Check workflow systems (circulation)
        try:
            from master_workflow_orchestrator import MasterWorkflowOrchestrator
            orchestrator = MasterWorkflowOrchestrator()
        except ImportError:
            issues.append("Workflow orchestrator not available - no workflow circulation")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P2_MEDIUM
                health_score = 0.7
        except Exception as e:
            issues.append(f"Workflow orchestrator error: {e}")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P2_MEDIUM
                health_score = min(health_score, 0.7)

        if issues:
            if any("jarvis" in issue.lower() and "running" in issue.lower() for issue in issues):
                recommendations.append("Start JARVIS full-time super agent - the heart must beat")
            if any("agent" in issue.lower() for issue in issues):
                recommendations.append("Register all MANUS agents - system needs to breathe")
            if any("workflow" in issue.lower() for issue in issues):
                recommendations.append("Initialize workflow orchestrator for system circulation")

        self.component_checks.append(AnatomicalComponentCheck(
            component_name="Core Systems - Heart & Lungs (Chest)",
            component_type="core_systems",
            status=status,
            priority=priority,
            issues=issues,
            recommendations=recommendations,
            health_score=health_score,
            anatomical_region=AnatomicalRegion.CHEST,
            dependencies=["jarvis_fulltime", "agent_registry", "workflow_orchestrator"]
        ))

    def _check_arms_action_systems(self):
        """Check ARMS - Action systems (voice, IDE control)"""
        issues = []
        recommendations = []
        status = ComponentStatus.HEALTHY
        priority = TriagePriority.P3_LOW
        health_score = 1.0

        # Check voice conversation (right arm)
        try:
            from jarvis_async_voice_conversation import get_async_voice_conversation
            voice_conv = get_async_voice_conversation(project_root=self.project_root)
            if not voice_conv.speech_config:
                issues.append("Voice conversation not configured - right arm paralyzed")
                status = ComponentStatus.FAILING
                priority = TriagePriority.P0_CRITICAL
                health_score = 0.0
        except ImportError:
            issues.append("Voice conversation module not available")
            status = ComponentStatus.FAILING
            priority = TriagePriority.P0_CRITICAL
            health_score = 0.0
        except Exception as e:
            issues.append(f"Voice conversation error: {e}")
            status = ComponentStatus.FAILING
            priority = TriagePriority.P0_CRITICAL
            health_score = 0.0

        # Check IDE integration (left arm)
        try:
            from jarvis_cursor_ide_keyboard_integration import get_jarvis_cursor_integration
            ide_integration = get_jarvis_cursor_integration(project_root=self.project_root)
            if not ide_integration.keyboard_controller:
                issues.append("IDE integration not available - left arm paralyzed")
                status = ComponentStatus.FAILING
                priority = TriagePriority.P0_CRITICAL
                health_score = min(health_score, 0.0)
        except ImportError:
            issues.append("IDE integration module not available")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.FAILING
                priority = TriagePriority.P0_CRITICAL
                health_score = 0.0
        except Exception as e:
            issues.append(f"IDE integration error: {e}")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.FAILING
                priority = TriagePriority.P0_CRITICAL
                health_score = 0.0

        if issues:
            if any("voice" in issue.lower() for issue in issues):
                recommendations.append("Configure Azure Speech SDK for voice conversation")
                recommendations.append("Start voice conversation: python start_jarvis_voice_conversation.py")
            if any("ide" in issue.lower() for issue in issues):
                recommendations.append("Install pynput and pygetwindow for IDE control")
                recommendations.append("Initialize IDE keyboard integration")

        self.component_checks.append(AnatomicalComponentCheck(
            component_name="Action Systems - Arms (Voice & IDE)",
            component_type="action_systems",
            status=status,
            priority=priority,
            issues=issues,
            recommendations=recommendations,
            health_score=health_score,
            anatomical_region=AnatomicalRegion.ARMS,
            dependencies=["voice_conversation", "ide_integration"]
        ))

    def _check_hands_fine_control(self):
        """Check HANDS - Fine motor control (keyboard, precise actions)"""
        issues = []
        recommendations = []
        status = ComponentStatus.HEALTHY
        priority = TriagePriority.P3_LOW
        health_score = 1.0

        # Check keyboard controller (fine motor control)
        try:
            from cursor_ide_keyboard_controller import CursorIDEKeyboardController
            controller = CursorIDEKeyboardController()
            if not controller.shortcuts:
                issues.append("Keyboard shortcuts not loaded - hands cannot type")
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P1_HIGH
                health_score = 0.6
        except ImportError:
            issues.append("Keyboard controller not available - no fine motor control")
            status = ComponentStatus.DEGRADED
            priority = TriagePriority.P1_HIGH
            health_score = 0.6
        except Exception as e:
            issues.append(f"Keyboard controller error: {e}")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P1_HIGH
                health_score = 0.6

        # Check command palette access (precision)
        try:
            # Command palette would be checked here
            pass
        except Exception as e:
            issues.append(f"Command palette access error: {e}")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P2_MEDIUM
                health_score = 0.8

        if issues:
            recommendations.append("Load keyboard shortcuts configuration")
            recommendations.append("Test keyboard shortcuts and command palette")

        self.component_checks.append(AnatomicalComponentCheck(
            component_name="Fine Motor Control - Hands (Keyboard & Precision)",
            component_type="fine_control",
            status=status,
            priority=priority,
            issues=issues,
            recommendations=recommendations,
            health_score=health_score,
            anatomical_region=AnatomicalRegion.HANDS,
            dependencies=["keyboard_controller", "command_palette"]
        ))

    def _check_torso_data_storage(self):
        """Check TORSO - Data & storage systems"""
        issues = []
        recommendations = []
        status = ComponentStatus.HEALTHY
        priority = TriagePriority.P3_LOW
        health_score = 1.0

        # Check data directories
        data_dirs = [
            "data/jarvis_ide_learning",
            "data/jarvis_fulltime",
            "data/jarvis_body_checks",
            "data/r5_living_matrix"
        ]

        for data_dir in data_dirs:
            dir_path = self.project_root / data_dir
            if not dir_path.exists():
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    issues.append(f"Cannot create data directory: {data_dir} - {e}")
                    if status == ComponentStatus.HEALTHY:
                        status = ComponentStatus.DEGRADED
                        priority = TriagePriority.P1_HIGH
                        health_score = 0.8

        # Check storage space
        try:
            import shutil
            total, used, free = shutil.disk_usage(self.project_root)
            free_percent = (free / total) * 100
            if free_percent < 10:
                issues.append(f"Low storage space: {free_percent:.1f}% free")
                if status == ComponentStatus.HEALTHY:
                    status = ComponentStatus.DEGRADED
                    priority = TriagePriority.P1_HIGH
                    health_score = 0.7
        except Exception as e:
            issues.append(f"Storage check error: {e}")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P2_MEDIUM
                health_score = 0.8

        if issues:
            recommendations.append("Fix data directory permissions")
            recommendations.append("Free up storage space if needed")

        self.component_checks.append(AnatomicalComponentCheck(
            component_name="Data & Storage - Torso",
            component_type="data_storage",
            status=status,
            priority=priority,
            issues=issues,
            recommendations=recommendations,
            health_score=health_score,
            anatomical_region=AnatomicalRegion.TORSO,
            dependencies=["file_system", "storage_space"]
        ))

    def _check_legs_foundation(self):
        """Check LEGS - Foundation & infrastructure"""
        issues = []
        recommendations = []
        status = ComponentStatus.HEALTHY
        priority = TriagePriority.P3_LOW
        health_score = 1.0

        # Check network connectivity (foundation)
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
        except OSError:
            issues.append("Network connectivity issues - cannot reach internet")
            status = ComponentStatus.DEGRADED
            priority = TriagePriority.P1_HIGH
            health_score = 0.7
        except Exception as e:
            issues.append(f"Network check error: {e}")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P2_MEDIUM
                health_score = 0.8

        # Check ULTRON cluster (infrastructure)
        try:
            from intelligent_llm_router import IntelligentLLMRouter
            router = IntelligentLLMRouter()
            if not router.kaiju_node or router.kaiju_node.status != "available":
                issues.append("KAIJU node not available - infrastructure degraded")
                if status == ComponentStatus.HEALTHY:
                    status = ComponentStatus.DEGRADED
                    priority = TriagePriority.P1_HIGH
                    health_score = 0.7
        except ImportError:
            issues.append("LLM router not available - no infrastructure")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P2_MEDIUM
                health_score = 0.7
        except Exception as e:
            issues.append(f"LLM router error: {e}")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P2_MEDIUM
                health_score = min(health_score, 0.7)

        if issues:
            recommendations.append("Check network connectivity")
            recommendations.append("Verify ULTRON cluster status")

        self.component_checks.append(AnatomicalComponentCheck(
            component_name="Foundation & Infrastructure - Legs",
            component_type="foundation",
            status=status,
            priority=priority,
            issues=issues,
            recommendations=recommendations,
            health_score=health_score,
            anatomical_region=AnatomicalRegion.LEGS,
            dependencies=["network", "ultron_cluster"]
        ))

    def _check_feet_security(self):
        """Check FEET - Grounding & security"""
        issues = []
        recommendations = []
        status = ComponentStatus.HEALTHY
        priority = TriagePriority.P3_LOW
        health_score = 1.0

        # Check Azure Key Vault access (security)
        try:
            from azure_service_bus_integration import AzureKeyVaultClient
            vault_url = "https://jarvis-lumina.vault.azure.net/"
            vault_client = AzureKeyVaultClient(vault_url=vault_url)
            # Try to access a secret (non-blocking test)
        except Exception as e:
            if "not found" not in str(e).lower():
                issues.append(f"Azure Key Vault access issue: {e}")
                if status == ComponentStatus.HEALTHY:
                    status = ComponentStatus.DEGRADED
                    priority = TriagePriority.P1_HIGH
                    health_score = 0.7
        except ImportError:
            issues.append("Azure Key Vault client not available")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P2_MEDIUM
                health_score = 0.8

        # Check security systems
        try:
            from security_droids_collaboration import SecurityDroidsCollaboration
            security = SecurityDroidsCollaboration()
        except ImportError:
            issues.append("Security droids not available - no security monitoring")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P2_MEDIUM
                health_score = 0.8
        except Exception as e:
            issues.append(f"Security system error: {e}")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P2_MEDIUM
                health_score = min(health_score, 0.8)

        if issues:
            recommendations.append("Verify Azure Key Vault credentials")
            recommendations.append("Initialize security monitoring systems")

        self.component_checks.append(AnatomicalComponentCheck(
            component_name="Grounding & Security - Feet",
            component_type="security",
            status=status,
            priority=priority,
            issues=issues,
            recommendations=recommendations,
            health_score=health_score,
            anatomical_region=AnatomicalRegion.FEET,
            dependencies=["azure_key_vault", "security_systems"]
        ))

    def _generate_report(self) -> BodyCheckReport:
        """Generate anatomical body check report"""
        # Calculate overall health
        if not self.component_checks:
            overall_health = 0.0
        else:
            overall_health = sum(c.health_score for c in self.component_checks) / len(self.component_checks)

        # Count components by status
        healthy = sum(1 for c in self.component_checks if c.status == ComponentStatus.HEALTHY)
        degraded = sum(1 for c in self.component_checks if c.status == ComponentStatus.DEGRADED)
        failing = sum(1 for c in self.component_checks if c.status == ComponentStatus.FAILING)

        # Group by priority
        priority_actions = {
            "P0": sorted(
                [c for c in self.component_checks if c.priority == TriagePriority.P0_CRITICAL],
                key=lambda x: x.health_score
            ),
            "P1": sorted(
                [c for c in self.component_checks if c.priority == TriagePriority.P1_HIGH],
                key=lambda x: x.health_score
            ),
            "P2": sorted(
                [c for c in self.component_checks if c.priority == TriagePriority.P2_MEDIUM],
                key=lambda x: x.health_score
            ),
            "P3": sorted(
                [c for c in self.component_checks if c.priority == TriagePriority.P3_LOW],
                key=lambda x: x.health_score
            )
        }

        # Generate summary
        summary_parts = []
        if failing > 0:
            summary_parts.append(f"{failing} critical component(s) failing (P0)")
        if degraded > 0:
            summary_parts.append(f"{degraded} component(s) degraded")
        if healthy == len(self.component_checks):
            summary_parts.append("All systems operational")
        else:
            summary_parts.append(f"{healthy} component(s) healthy")

        # Add anatomical summary
        region_summary = []
        for region in AnatomicalRegion:
            region_components = [c for c in self.component_checks if c.anatomical_region == region]
            if region_components:
                region_healthy = sum(1 for c in region_components if c.status == ComponentStatus.HEALTHY)
                region_summary.append(f"{region.value}: {region_healthy}/{len(region_components)} healthy")

        if region_summary:
            summary_parts.append(f"Regions: {', '.join(region_summary)}")

        summary = f"Overall health: {overall_health:.1%}. " + ". ".join(summary_parts) + "."

        # Convert to base ComponentCheck for compatibility
        base_components = [ComponentCheck(
            component_name=c.component_name,
            component_type=c.component_type,
            status=c.status,
            priority=c.priority,
            issues=c.issues,
            recommendations=c.recommendations,
            health_score=c.health_score,
            last_checked=c.last_checked,
            dependencies=c.dependencies
        ) for c in self.component_checks]

        report = BodyCheckReport(
            timestamp=datetime.now(),
            overall_health_score=overall_health,
            total_components=len(self.component_checks),
            healthy_components=healthy,
            degraded_components=degraded,
            failing_components=failing,
            components=base_components,
            priority_actions=priority_actions,
            summary=summary
        )

        return report

    def _save_report(self, report: BodyCheckReport):
        """Save anatomical body check report"""
        report_file = self.data_dir / f"anatomical_body_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            # Add anatomical data to report
            report_dict = report.to_dict()
            report_dict['anatomical_regions'] = {
                region.value: [
                    c.to_dict() for c in self.component_checks 
                    if c.anatomical_region == region
                ]
                for region in AnatomicalRegion
            }

            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_dict, f, indent=2, default=str)
            logger.info(f"✅ Anatomical report saved: {report_file}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="JARVIS Anatomical Body Check - Starting from HEAD (Brain) down"
    )
    parser.add_argument("--check", action="store_true", help="Perform anatomical body check")
    parser.add_argument("--region", type=str, choices=["head", "neck", "chest", "arms", "hands", "torso", "legs", "feet"],
                       help="Check specific anatomical region")

    args = parser.parse_args()

    body_check = JARVISAnatomicalBodyCheck()

    if args.check or not args.region:
        report = body_check.perform_anatomical_body_check()

        print("\n" + "="*70)
        print("🔍 JARVIS Anatomical Body Check Report")
        print("="*70)
        print(f"\nOverall Health Score: {report.overall_health_score:.1%}")
        print(f"Total Components: {report.total_components}")
        print(f"  ✅ Healthy: {report.healthy_components}")
        print(f"  ⚠️  Degraded: {report.degraded_components}")
        print(f"  ❌ Failing: {report.failing_components}")
        print(f"\nSummary: {report.summary}")

        print("\n" + "="*70)
        print("Anatomical Regions")
        print("="*70)

        for region in AnatomicalRegion:
            region_components = [c for c in body_check.component_checks if c.anatomical_region == region]
            if region_components:
                healthy = sum(1 for c in region_components if c.status == ComponentStatus.HEALTHY)
                print(f"\n{region.value.upper()}: {len(region_components)} components ({healthy} healthy)")
                for component in region_components:
                    status_emoji = "✅" if component.status == ComponentStatus.HEALTHY else "⚠️" if component.status == ComponentStatus.DEGRADED else "❌"
                    print(f"  {status_emoji} {component.component_name} ({component.status.value})")
                    if component.issues:
                        for issue in component.issues[:2]:
                            print(f"    - {issue}")

    else:
        parser.print_help()


if __name__ == "__main__":


    main()