#!/usr/bin/env python3
"""
JARVIS Body Check with Triage
MANUS Framework - Comprehensive Self-Assessment and Priority Determination

JARVIS performs a complete "body check" of all systems, components, and capabilities,
identifying what needs the most work with triage-based prioritization.

Features:
- Comprehensive system health audit
- Component-by-component assessment
- Triage-based prioritization (P0/P1/P2/P3)
- Actionable recommendations
- Priority-ordered action plan

@JARVIS @MANUS @TRIAGE @SYPHON
"""

import sys
import json
import time
import subprocess
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

logger = get_logger("JARVISBodyCheckTriage")


class TriagePriority(Enum):
    """Triage priority levels"""
    P0_CRITICAL = "P0"  # Critical - Do immediately
    P1_HIGH = "P1"     # High - Within 30 days
    P2_MEDIUM = "P2"   # Medium - Within 60-90 days
    P3_LOW = "P3"      # Low - Ongoing/standard


class ComponentStatus(Enum):
    """Component health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILING = "failing"
    UNKNOWN = "unknown"
    NOT_INITIALIZED = "not_initialized"


@dataclass
class ComponentCheck:
    """Result of checking a single component"""
    component_name: str
    component_type: str
    status: ComponentStatus
    priority: TriagePriority
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    health_score: float = 0.0  # 0.0 to 1.0
    last_checked: datetime = field(default_factory=datetime.now)
    dependencies: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['status'] = self.status.value
        data['priority'] = self.priority.value
        data['last_checked'] = self.last_checked.isoformat()
        return data


@dataclass
class BodyCheckReport:
    """Complete body check report"""
    timestamp: datetime
    overall_health_score: float
    total_components: int
    healthy_components: int
    degraded_components: int
    failing_components: int
    components: List[ComponentCheck] = field(default_factory=list)
    priority_actions: Dict[str, List[ComponentCheck]] = field(default_factory=dict)
    summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['components'] = [c.to_dict() for c in self.components]
        data['priority_actions'] = {
            priority: [c.to_dict() for c in checks]
            for priority, checks in self.priority_actions.items()
        }
        return data


class JARVISBodyCheckTriage:
    """
    JARVIS Body Check with Triage System

    Performs comprehensive self-assessment of all JARVIS systems
    and prioritizes issues using triage system.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize body check system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = logger

        # Data directory
        self.data_dir = self.project_root / "data" / "jarvis_body_checks"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Component registry
        self.component_checks: List[ComponentCheck] = []

        logger.info("✅ JARVIS Body Check Triage System initialized")

    def perform_body_check(self) -> BodyCheckReport:
        """
        Perform comprehensive body check of all JARVIS systems

        Returns:
            BodyCheckReport with complete assessment
        """
        logger.info("🔍 Starting JARVIS body check...")
        logger.info("   Assessing all systems, components, and capabilities")

        self.component_checks = []

        # Check all major components
        self._check_voice_systems()
        self._check_ide_integration()
        self._check_agent_systems()
        self._check_learning_systems()
        self._check_communication_systems()
        self._check_storage_systems()
        self._check_security_systems()
        self._check_monitoring_systems()
        self._check_workflow_systems()
        self._check_data_systems()
        self._check_integration_systems()

        # Generate report
        report = self._generate_report()

        # Save report
        self._save_report(report)

        logger.info("✅ Body check complete")
        logger.info(f"   Overall Health Score: {report.overall_health_score:.2%}")
        logger.info(f"   Priority Actions: P0={len(report.priority_actions.get('P0', []))}, "
                   f"P1={len(report.priority_actions.get('P1', []))}, "
                   f"P2={len(report.priority_actions.get('P2', []))}, "
                   f"P3={len(report.priority_actions.get('P3', []))}")

        return report

    def _check_voice_systems(self):
        """Check voice conversation and recognition systems"""
        logger.debug("   Checking voice systems...")

        issues = []
        recommendations = []
        status = ComponentStatus.HEALTHY
        priority = TriagePriority.P3_LOW
        health_score = 1.0

        # Check async voice conversation
        try:
            from jarvis_async_voice_conversation import get_async_voice_conversation
            voice_conv = get_async_voice_conversation(project_root=self.project_root)
            if not voice_conv.speech_config:
                issues.append("Azure Speech SDK not configured - voice conversation unavailable")
                status = ComponentStatus.FAILING
                priority = TriagePriority.P0_CRITICAL  # Critical for hands-free operation
                health_score = 0.0
            elif not voice_conv.azure_speech_key:
                issues.append("Azure Speech key missing - cannot initialize voice")
                status = ComponentStatus.FAILING
                priority = TriagePriority.P0_CRITICAL
                health_score = 0.0
            elif not voice_conv.running:
                issues.append("Voice conversation not running - needs to be started")
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P1_HIGH
                health_score = 0.5
        except ImportError:
            issues.append("Voice conversation module not available")
            status = ComponentStatus.FAILING
            priority = TriagePriority.P0_CRITICAL
            health_score = 0.0
        except Exception as e:
            issues.append(f"Voice conversation system error: {e}")
            status = ComponentStatus.FAILING
            priority = TriagePriority.P0_CRITICAL
            health_score = 0.0

        # Check always-listening
        try:
            from jarvis_always_listening import JARVISAlwaysListening
            listener = JARVISAlwaysListening(project_root=self.project_root)
            if not listener.continuous_recognizer:
                issues.append("Always-listening recognizer not initialized")
                if status == ComponentStatus.HEALTHY:
                    status = ComponentStatus.DEGRADED
                    priority = TriagePriority.P1_HIGH
                    health_score = 0.6
        except ImportError:
            if status == ComponentStatus.HEALTHY:
                issues.append("Always-listening module not available")
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P1_HIGH
                health_score = min(health_score, 0.7)
        except Exception as e:
            issues.append(f"Always-listening error: {e}")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P1_HIGH
                health_score = min(health_score, 0.6)

        # Check TTS system
        try:
            from hybrid_tts_system import HybridTTSSystem
            # TTS system exists
        except ImportError:
            issues.append("TTS system not available - voice responses may not work")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P1_HIGH
                health_score = min(health_score, 0.7)

        # Recommendations
        if issues:
            if any("Azure Speech" in issue or "Speech SDK" in issue for issue in issues):
                recommendations.append("Configure Azure Speech SDK credentials in Key Vault")
                recommendations.append("Set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION environment variables")
            if any("microphone" in issue.lower() or "listening" in issue.lower() for issue in issues):
                recommendations.append("Verify microphone permissions and connectivity")
                recommendations.append("Test voice recognition with simple commands")
            recommendations.append("Start voice conversation system: python start_jarvis_voice_conversation.py")

        self.component_checks.append(ComponentCheck(
            component_name="Voice Conversation System",
            component_type="voice",
            status=status,
            priority=priority,
            issues=issues,
            recommendations=recommendations,
            health_score=health_score,
            dependencies=["azure_speech_sdk", "microphone", "tts_system"]
        ))

    def _check_ide_integration(self):
        """Check Cursor IDE integration systems"""
        logger.debug("   Checking IDE integration...")

        issues = []
        recommendations = []
        status = ComponentStatus.HEALTHY
        priority = TriagePriority.P3_LOW
        health_score = 1.0

        # Check keyboard integration
        try:
            from jarvis_cursor_ide_keyboard_integration import get_jarvis_cursor_integration
            integration = get_jarvis_cursor_integration(project_root=self.project_root)
            if not integration.keyboard_controller:
                issues.append("Keyboard controller not available - pynput/pygetwindow missing")
                status = ComponentStatus.FAILING
                priority = TriagePriority.P0_CRITICAL  # Critical for hands-free operation
                health_score = 0.0
            elif not integration.command_mappings:
                issues.append("Command mappings not loaded - keyboard shortcuts unavailable")
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P1_HIGH
                health_score = 0.5
        except ImportError as e:
            issues.append(f"IDE integration module not available: {e}")
            status = ComponentStatus.FAILING
            priority = TriagePriority.P0_CRITICAL
            health_score = 0.0
        except Exception as e:
            issues.append(f"IDE integration error: {e}")
            status = ComponentStatus.FAILING
            priority = TriagePriority.P0_CRITICAL
            health_score = 0.0

        # Check interaction learner
        try:
            from jarvis_ide_interaction_learner import get_ide_learner
            learner = get_ide_learner(project_root=self.project_root)
            if len(learner.feature_patterns) == 0:
                issues.append("No learned patterns yet - system needs training data from usage")
                if status == ComponentStatus.HEALTHY:
                    status = ComponentStatus.DEGRADED
                    priority = TriagePriority.P2_MEDIUM
                    health_score = 0.7
            elif len(learner.feature_patterns) < 10:
                issues.append("Insufficient learning data - only {len(learner.feature_patterns)} patterns learned")
                if status == ComponentStatus.HEALTHY:
                    status = ComponentStatus.DEGRADED
                    priority = TriagePriority.P2_MEDIUM
                    health_score = 0.8
        except ImportError:
            issues.append("Interaction learner module not available")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P2_MEDIUM
                health_score = 0.7
        except Exception as e:
            issues.append(f"Interaction learner error: {e}")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P2_MEDIUM
                health_score = min(health_score, 0.7)

        # Check feature-agent mapper
        try:
            from jarvis_ide_feature_agent_mapper import JARVISIDEFeatureAgentMapper
            mapper = JARVISIDEFeatureAgentMapper(project_root=self.project_root)
            if len(mapper.feature_categories) == 0:
                issues.append("No feature categories defined - agent mapping unavailable")
                if status == ComponentStatus.HEALTHY:
                    status = ComponentStatus.DEGRADED
                    priority = TriagePriority.P2_MEDIUM
                    health_score = 0.7
        except ImportError:
            issues.append("Feature-agent mapper not available")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P2_MEDIUM
                health_score = min(health_score, 0.8)
        except Exception as e:
            issues.append(f"Feature-agent mapper error: {e}")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P2_MEDIUM
                health_score = min(health_score, 0.8)

        # Recommendations
        if issues:
            if any("pynput" in issue.lower() or "keyboard" in issue.lower() for issue in issues):
                recommendations.append("Install dependencies: pip install pynput pygetwindow")
                recommendations.append("Verify Cursor IDE is running and accessible")
            if any("learning" in issue.lower() or "pattern" in issue.lower() for issue in issues):
                recommendations.append("Start tracking IDE interactions: learner.start_tracking()")
                recommendations.append("Use IDE commands to build learning data")
            recommendations.append("Test keyboard shortcuts: python scripts/python/cursor_ide_keyboard_controller.py --command 'open chat'")

        self.component_checks.append(ComponentCheck(
            component_name="Cursor IDE Integration",
            component_type="ide_integration",
            status=status,
            priority=priority,
            issues=issues,
            recommendations=recommendations,
            health_score=health_score,
            dependencies=["pynput", "pygetwindow", "cursor_ide", "interaction_learner"]
        ))

    def _check_agent_systems(self):
        """Check MANUS agent systems"""
        logger.debug("   Checking agent systems...")

        issues = []
        recommendations = []
        status = ComponentStatus.HEALTHY
        priority = TriagePriority.P3_LOW
        health_score = 1.0

        # Check agent registry
        agents_config = self.project_root / "config" / "agent_communication" / "agents.json"
        if not agents_config.exists():
            issues.append("Agent registry not found - cannot assign agents to features")
            status = ComponentStatus.FAILING
            priority = TriagePriority.P0_CRITICAL  # Critical for agent assignment
            health_score = 0.0
        else:
            try:
                with open(agents_config, 'r') as f:
                    agents = json.load(f)
                    if len(agents) == 0:
                        issues.append("No agents registered in registry")
                        status = ComponentStatus.FAILING
                        priority = TriagePriority.P0_CRITICAL
                        health_score = 0.0
                    else:
                        # Check for key agents
                        required_agents = ["r2d2", "c3po", "k2so", "2-1b", "ig88", "mousedroid", "uatu"]
                        missing_agents = [agent for agent in required_agents if agent not in agents]
                        if missing_agents:
                            issues.append(f"Missing key agents: {', '.join(missing_agents)}")
                            if status == ComponentStatus.HEALTHY:
                                status = ComponentStatus.DEGRADED
                                priority = TriagePriority.P1_HIGH
                                health_score = 0.7
            except Exception as e:
                issues.append(f"Error reading agent registry: {e}")
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P1_HIGH
                health_score = 0.6

        # Check JARVIS full-time super agent
        try:
            from jarvis_fulltime_super_agent import get_jarvis_fulltime
            jarvis = get_jarvis_fulltime(project_root=self.project_root)
            if not jarvis.running:
                issues.append("JARVIS full-time super agent not running")
                if status == ComponentStatus.HEALTHY:
                    status = ComponentStatus.DEGRADED
                    priority = TriagePriority.P1_HIGH
                    health_score = 0.7
        except ImportError:
            issues.append("JARVIS full-time super agent module not available")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P1_HIGH
                health_score = 0.7
        except Exception as e:
            issues.append(f"JARVIS full-time super agent error: {e}")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P1_HIGH
                health_score = min(health_score, 0.7)

        # Check droid actor system
        try:
            from droid_actor_system import DroidActorSystem
            droid_system = DroidActorSystem()
            if not droid_system.droids:
                issues.append("Droid actor system has no droids registered")
                if status == ComponentStatus.HEALTHY:
                    status = ComponentStatus.DEGRADED
                    priority = TriagePriority.P1_HIGH
                    health_score = 0.6
            elif len(droid_system.droids) < 5:
                issues.append(f"Only {len(droid_system.droids)} droids registered - expected more")
                if status == ComponentStatus.HEALTHY:
                    status = ComponentStatus.DEGRADED
                    priority = TriagePriority.P2_MEDIUM
                    health_score = 0.8
        except ImportError:
            issues.append("Droid actor system module not available")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P2_MEDIUM
                health_score = 0.7
        except Exception as e:
            issues.append(f"Droid actor system error: {e}")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P2_MEDIUM
                health_score = min(health_score, 0.7)

        # Recommendations
        if issues:
            if any("registry" in issue.lower() or "agent" in issue.lower() for issue in issues):
                recommendations.append("Create/update agent registry: config/agent_communication/agents.json")
                recommendations.append("Register all MANUS agents (R2-D2, C-3PO, K-2SO, 2-1B, IG-88, MouseDroid, Uatu)")
            if any("jarvis" in issue.lower() and "running" in issue.lower() for issue in issues):
                recommendations.append("Start JARVIS full-time super agent")
            if any("droid" in issue.lower() for issue in issues):
                recommendations.append("Initialize droid actor system with all droids")
            recommendations.append("Test agent communication and coordination")

        self.component_checks.append(ComponentCheck(
            component_name="MANUS Agent System",
            component_type="agents",
            status=status,
            priority=priority,
            issues=issues,
            recommendations=recommendations,
            health_score=health_score,
            dependencies=["agent_registry", "jarvis_fulltime", "droid_system"]
        ))

    def _check_learning_systems(self):
        """Check learning and pattern recognition systems"""
        logger.debug("   Checking learning systems...")

        issues = []
        recommendations = []
        status = ComponentStatus.HEALTHY
        priority = TriagePriority.P3_LOW
        health_score = 1.0

        # Check interaction learner
        try:
            from jarvis_ide_interaction_learner import get_ide_learner
            learner = get_ide_learner(project_root=self.project_root)
            if len(learner.feature_patterns) < 10:
                issues.append("Insufficient learning data - need more interactions")
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P2_MEDIUM
                health_score = 0.7
        except Exception as e:
            issues.append(f"Interaction learner error: {e}")
            status = ComponentStatus.DEGRADED
            priority = TriagePriority.P2_MEDIUM
            health_score = 0.6

        # Check feature-agent mappings
        try:
            from jarvis_ide_feature_agent_mapper import JARVISIDEFeatureAgentMapper
            mapper = JARVISIDEFeatureAgentMapper(project_root=self.project_root)
            if len(mapper.feature_categories) == 0:
                issues.append("No feature categories defined")
                if status == ComponentStatus.HEALTHY:
                    status = ComponentStatus.DEGRADED
                    priority = TriagePriority.P2_MEDIUM
                    health_score = 0.7
        except Exception as e:
            issues.append(f"Feature-agent mapper error: {e}")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P2_MEDIUM
                health_score = min(health_score, 0.7)

        # Recommendations
        if issues:
            recommendations.append("Start tracking IDE interactions to build learning data")
            recommendations.append("Define comprehensive feature categories")
            recommendations.append("Build feature-to-agent mapping database")

        self.component_checks.append(ComponentCheck(
            component_name="Learning & Pattern Systems",
            component_type="learning",
            status=status,
            priority=priority,
            issues=issues,
            recommendations=recommendations,
            health_score=health_score,
            dependencies=["interaction_learner", "feature_mapper"]
        ))

    def _check_communication_systems(self):
        """Check communication and bridge systems"""
        logger.debug("   Checking communication systems...")

        issues = []
        recommendations = []
        status = ComponentStatus.HEALTHY
        priority = TriagePriority.P3_LOW
        health_score = 1.0

        # Check JARVIS bridge
        try:
            from jarvis_communication_bridge import get_jarvis_bridge
            bridge = get_jarvis_bridge()
            if not bridge:
                issues.append("JARVIS communication bridge not available")
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P2_MEDIUM
                health_score = 0.7
        except Exception as e:
            issues.append(f"Communication bridge error: {e}")
            status = ComponentStatus.DEGRADED
            priority = TriagePriority.P2_MEDIUM
            health_score = 0.6

        # Recommendations
        if issues:
            recommendations.append("Initialize JARVIS communication bridge")
            recommendations.append("Test inter-agent communication")

        self.component_checks.append(ComponentCheck(
            component_name="Communication Systems",
            component_type="communication",
            status=status,
            priority=priority,
            issues=issues,
            recommendations=recommendations,
            health_score=health_score,
            dependencies=["communication_bridge"]
        ))

    def _check_storage_systems(self):
        """Check data storage and persistence systems"""
        logger.debug("   Checking storage systems...")

        issues = []
        recommendations = []
        status = ComponentStatus.HEALTHY
        priority = TriagePriority.P3_LOW
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
                    issues.append(f"Cannot create data directory: {data_dir} - {e}")
                    if status == ComponentStatus.HEALTHY:
                        status = ComponentStatus.DEGRADED
                        priority = TriagePriority.P1_HIGH
                        health_score = 0.8

        # Recommendations
        if issues:
            recommendations.append("Fix data directory permissions")
            recommendations.append("Verify storage space availability")

        self.component_checks.append(ComponentCheck(
            component_name="Storage Systems",
            component_type="storage",
            status=status,
            priority=priority,
            issues=issues,
            recommendations=recommendations,
            health_score=health_score,
            dependencies=["file_system", "permissions"]
        ))

    def _check_security_systems(self):
        """Check security and access control systems"""
        logger.debug("   Checking security systems...")

        issues = []
        recommendations = []
        status = ComponentStatus.HEALTHY
        priority = TriagePriority.P3_LOW
        health_score = 1.0

        # Check Azure Key Vault access
        try:
            from azure_service_bus_integration import AzureKeyVaultClient
            vault_url = "https://jarvis-lumina.vault.azure.net/"
            vault_client = AzureKeyVaultClient(vault_url=vault_url)
            # Try to access a secret (non-blocking test)
            # This would be a lightweight check
        except Exception as e:
            issues.append(f"Azure Key Vault access issue: {e}")
            if "not found" not in str(e).lower():
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P1_HIGH
                health_score = 0.7

        # Recommendations
        if issues:
            recommendations.append("Verify Azure Key Vault credentials")
            recommendations.append("Check security key access permissions")

        self.component_checks.append(ComponentCheck(
            component_name="Security Systems",
            component_type="security",
            status=status,
            priority=priority,
            issues=issues,
            recommendations=recommendations,
            health_score=health_score,
            dependencies=["azure_key_vault", "credentials"]
        ))

    def _check_monitoring_systems(self):
        """Check monitoring and diagnostics systems"""
        logger.debug("   Checking monitoring systems...")

        issues = []
        recommendations = []
        status = ComponentStatus.HEALTHY
        priority = TriagePriority.P3_LOW
        health_score = 1.0

        # Check if monitoring is active
        # This would check for active monitoring threads/processes

        # Recommendations
        if issues:
            recommendations.append("Enable comprehensive monitoring")
            recommendations.append("Set up alerting for critical issues")

        self.component_checks.append(ComponentCheck(
            component_name="Monitoring Systems",
            component_type="monitoring",
            status=status,
            priority=priority,
            issues=issues,
            recommendations=recommendations,
            health_score=health_score,
            dependencies=["monitoring_threads"]
        ))

    def _check_workflow_systems(self):
        """Check workflow and orchestration systems"""
        logger.debug("   Checking workflow systems...")

        issues = []
        recommendations = []
        status = ComponentStatus.HEALTHY
        priority = TriagePriority.P3_LOW
        health_score = 1.0

        # Check workflow systems
        # This would verify workflow engines, n8n integration, etc.

        self.component_checks.append(ComponentCheck(
            component_name="Workflow Systems",
            component_type="workflow",
            status=status,
            priority=priority,
            issues=issues,
            recommendations=recommendations,
            health_score=health_score,
            dependencies=["workflow_engine"]
        ))

    def _check_data_systems(self):
        """Check data processing and analysis systems"""
        logger.debug("   Checking data systems...")

        issues = []
        recommendations = []
        status = ComponentStatus.HEALTHY
        priority = TriagePriority.P3_LOW
        health_score = 1.0

        # Check R5 system
        try:
            from r5_living_context_matrix import R5LivingContextMatrix
            r5 = R5LivingContextMatrix(project_root=self.project_root)
        except Exception as e:
            issues.append(f"R5 system error: {e}")
            status = ComponentStatus.DEGRADED
            priority = TriagePriority.P2_MEDIUM
            health_score = 0.7

        self.component_checks.append(ComponentCheck(
            component_name="Data Systems",
            component_type="data",
            status=status,
            priority=priority,
            issues=issues,
            recommendations=recommendations,
            health_score=health_score,
            dependencies=["r5_system"]
        ))

    def _check_integration_systems(self):
        """Check external integrations"""
        logger.debug("   Checking integration systems...")

        issues = []
        recommendations = []
        status = ComponentStatus.HEALTHY
        priority = TriagePriority.P3_LOW
        health_score = 1.0

        # Check ULTRON cluster
        try:
            from intelligent_llm_router import IntelligentLLMRouter
            router = IntelligentLLMRouter()
            if not router.kaiju_node or router.kaiju_node.status != "available":
                issues.append("KAIJU node not available")
                if status == ComponentStatus.HEALTHY:
                    status = ComponentStatus.DEGRADED
                    priority = TriagePriority.P1_HIGH
                    health_score = 0.7
        except Exception as e:
            issues.append(f"ULTRON cluster error: {e}")
            if status == ComponentStatus.HEALTHY:
                status = ComponentStatus.DEGRADED
                priority = TriagePriority.P2_MEDIUM
                health_score = 0.7

        self.component_checks.append(ComponentCheck(
            component_name="Integration Systems",
            component_type="integration",
            status=status,
            priority=priority,
            issues=issues,
            recommendations=recommendations,
            health_score=health_score,
            dependencies=["ultron_cluster", "llm_router"]
        ))

    def _generate_report(self) -> BodyCheckReport:
        """Generate comprehensive body check report"""
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
            "P0": [c for c in self.component_checks if c.priority == TriagePriority.P0_CRITICAL],
            "P1": [c for c in self.component_checks if c.priority == TriagePriority.P1_HIGH],
            "P2": [c for c in self.component_checks if c.priority == TriagePriority.P2_MEDIUM],
            "P3": [c for c in self.component_checks if c.priority == TriagePriority.P3_LOW]
        }

        # Generate summary
        summary_parts = []
        if failing > 0:
            summary_parts.append(f"{failing} critical component(s) failing")
        if degraded > 0:
            summary_parts.append(f"{degraded} component(s) degraded")
        if healthy == len(self.component_checks):
            summary_parts.append("All systems operational")
        else:
            summary_parts.append(f"{healthy} component(s) healthy")

        summary = f"Overall health: {overall_health:.1%}. " + ". ".join(summary_parts) + "."

        report = BodyCheckReport(
            timestamp=datetime.now(),
            overall_health_score=overall_health,
            total_components=len(self.component_checks),
            healthy_components=healthy,
            degraded_components=degraded,
            failing_components=failing,
            components=self.component_checks.copy(),
            priority_actions=priority_actions,
            summary=summary
        )

        return report

    def _save_report(self, report: BodyCheckReport):
        """Save body check report"""
        report_file = self.data_dir / f"body_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report.to_dict(), f, indent=2, default=str)
            logger.info(f"✅ Report saved: {report_file}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")

    def get_priority_action_plan(self, report: Optional[BodyCheckReport] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Get prioritized action plan from body check"""
        if report is None:
            report = self.perform_body_check()

        action_plan = {}

        for priority in ["P0", "P1", "P2", "P3"]:
            components = report.priority_actions.get(priority, [])
            action_plan[priority] = []

            for component in components:
                # Add issues as actions
                for issue in component.issues:
                    action_plan[priority].append({
                        "action": f"Fix: {issue}",
                        "component": component.component_name,
                        "priority": priority,
                        "health_score": component.health_score,
                        "status": component.status.value
                    })

                # Add recommendations as actions
                for rec in component.recommendations:
                    action_plan[priority].append({
                        "action": rec,
                        "component": component.component_name,
                        "priority": priority,
                        "health_score": component.health_score,
                        "status": component.status.value
                    })

            # Sort by health score (worst first)
            action_plan[priority].sort(key=lambda x: x.get("health_score", 1.0))

        return action_plan

    def get_top_priorities(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top priority actions across all levels"""
        report = self.perform_body_check()
        action_plan = self.get_priority_action_plan(report)

        top_priorities = []

        # Get P0 first
        for action in action_plan.get("P0", [])[:limit]:
            top_priorities.append(action)

        # Then P1
        remaining = limit - len(top_priorities)
        if remaining > 0:
            for action in action_plan.get("P1", [])[:remaining]:
                top_priorities.append(action)

        # Then P2 if still room
        remaining = limit - len(top_priorities)
        if remaining > 0:
            for action in action_plan.get("P2", [])[:remaining]:
                top_priorities.append(action)

        return top_priorities


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="JARVIS Body Check with Triage - Comprehensive self-assessment"
    )
    parser.add_argument("--check", action="store_true", help="Perform body check")
    parser.add_argument("--report", action="store_true", help="Show detailed report")
    parser.add_argument("--actions", action="store_true", help="Show priority action plan")
    parser.add_argument("--priority", type=str, choices=["P0", "P1", "P2", "P3"],
                       help="Filter by priority level")

    args = parser.parse_args()

    body_check = JARVISBodyCheckTriage()

    if args.check or not any([args.report, args.actions]):
        report = body_check.perform_body_check()

        print("\n" + "="*70)
        print("🔍 JARVIS Body Check Report")
        print("="*70)
        print(f"\nOverall Health Score: {report.overall_health_score:.1%}")
        print(f"Total Components: {report.total_components}")
        print(f"  ✅ Healthy: {report.healthy_components}")
        print(f"  ⚠️  Degraded: {report.degraded_components}")
        print(f"  ❌ Failing: {report.failing_components}")
        print(f"\nSummary: {report.summary}")

        if args.report or args.actions:
            print("\n" + "="*70)
            print("Priority Actions")
            print("="*70)

            for priority in ["P0", "P1", "P2", "P3"]:
                components = report.priority_actions.get(priority, [])
                if components:
                    print(f"\n{priority} ({len(components)} components):")
                    for component in components:
                        print(f"  • {component.component_name} ({component.status.value})")
                        if component.issues:
                            for issue in component.issues:
                                print(f"    - Issue: {issue}")
                        if component.recommendations:
                            for rec in component.recommendations[:2]:  # Show first 2
                                print(f"    - {rec}")

        if args.actions:
            action_plan = body_check.get_priority_action_plan(report)
            print("\n" + "="*70)
            print("Action Plan")
            print("="*70)

            for priority in ["P0", "P1", "P2", "P3"]:
                actions = action_plan.get(priority, [])
                if actions:
                    print(f"\n{priority} Actions ({len(actions)}):")
                    for action in actions[:5]:  # Show first 5
                        print(f"  • {action['action']}")
                    if len(actions) > 5:
                        print(f"    ... and {len(actions) - 5} more")

    else:
        parser.print_help()


if __name__ == "__main__":


    main()