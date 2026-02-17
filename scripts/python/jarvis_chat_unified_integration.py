#!/usr/bin/env python3
"""
JARVIS Chat Unified Integration - All Frameworks & Subagents

Integrates all Lumina frameworks, systems, and subagents into JARVIS Chat,
providing a single interface to the complete ecosystem.

See: docs/system/JARVIS_CHAT_CA_FIDELITY_SPEC.md

Author: Lumina AI Team
Date: 2026-02-03
Tags: @PEAK @JARVIS @FRAMEWORK @SUBAGENT #integration #automation
"""

import json
import logging
import sys
import threading
import queue
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("JarvisUnifiedIntegration")

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts" / "python"
sys.path.insert(0, str(SCRIPTS_DIR))


# =============================================================================
# FRAMEWORK REGISTRY - All Available Frameworks
# =============================================================================

class FrameworkCategory(Enum):
    """Categories of frameworks"""
    WORKFLOW = "workflow"
    VOICE = "voice"
    AGENT = "agent"
    AI = "ai"
    SECURITY = "security"
    PLATFORM = "platform"
    COLLABORATION = "collaboration"
    AUTOMATION = "automation"
    DECISION = "decision"
    MONITORING = "monitoring"


@dataclass
class FrameworkInfo:
    """Information about a framework"""
    name: str
    module: str
    category: FrameworkCategory
    description: str
    class_name: str
    available: bool = False
    instance: Any = None


# Framework registry - lazy loaded
FRAMEWORK_REGISTRY: Dict[str, FrameworkInfo] = {
    # Workflow Frameworks
    "water_workflow": FrameworkInfo(
        name="Water Workflow System",
        module="water_workflow_system",
        category=FrameworkCategory.WORKFLOW,
        description="Be like water - flow autonomously or escalate",
        class_name="WaterWorkflowSystem",
    ),
    "workflow_functionality": FrameworkInfo(
        name="Workflow Functionality Framework",
        module="workflow_functionality_framework",
        category=FrameworkCategory.WORKFLOW,
        description="Core workflow execution and management",
        class_name="WorkflowFunctionalityFramework",
    ),
    
    # Voice Frameworks
    "voice_systems": FrameworkInfo(
        name="Voice Systems Test Framework",
        module="voice_systems_test_framework",
        category=FrameworkCategory.VOICE,
        description="Testing and validation for voice systems",
        class_name="VoiceSystemsTestFramework",
    ),
    "hybrid_voice": FrameworkInfo(
        name="Hybrid Macro Voice Framework",
        module="hybrid_macro_voice_framework",
        category=FrameworkCategory.VOICE,
        description="Hybrid voice commands and macro integration",
        class_name="HybridMacroVoiceFramework",
    ),
    
    # Agent Frameworks
    "agent_orchestrator": FrameworkInfo(
        name="JARVIS Agent Orchestrator",
        module="jarvis_agent_orchestrator",
        category=FrameworkCategory.AGENT,
        description="Orchestrates agents across AI systems",
        class_name="JARVISAgentOrchestrator",
    ),
    "subagent_delegation": FrameworkInfo(
        name="JARVIS Subagent Delegation",
        module="jarvis_subagent_delegation",
        category=FrameworkCategory.AGENT,
        description="Delegates work to specialized subagents",
        class_name="JARVISSubagentDelegation",
    ),
    "dynamic_spawner": FrameworkInfo(
        name="Dynamic Subagent Spawner",
        module="dynamic_subagent_spawner",
        category=FrameworkCategory.AGENT,
        description="Predictive agent spawning using psychohistory",
        class_name="DynamicSubagentSpawner",
    ),
    "super_agent_backstories": FrameworkInfo(
        name="Super Agent Backstories",
        module="super_agent_backstories",
        category=FrameworkCategory.AGENT,
        description="Character development for super agents",
        class_name="SuperAgentBackstorySystem",
    ),
    
    # AI Frameworks
    "jarvis_agi": FrameworkInfo(
        name="JARVIS AGI Framework",
        module="jarvis_agi_framework",
        category=FrameworkCategory.AI,
        description="Artificial General Intelligence foundations",
        class_name="JARVISAGIFramework",
    ),
    "local_ai_bridge": FrameworkInfo(
        name="Local AI Context Bridge",
        module="local_ai_context_bridge",
        category=FrameworkCategory.AI,
        description="Routes AI requests to local clusters",
        class_name="LocalAIContextBridge",
    ),
    "bitnet_inference": FrameworkInfo(
        name="BitNet Inference",
        module="bitnet_inference",
        category=FrameworkCategory.AI,
        description="CPU-based 1-bit LLM inference",
        class_name="BitNetInference",
    ),
    "three_tier_ai": FrameworkInfo(
        name="Three Tier AI System",
        module="three_tier_ai_system",
        category=FrameworkCategory.AI,
        description="Tiered AI routing (local/cloud/premium)",
        class_name="ThreeTierAISystem",
    ),
    
    # Security Frameworks
    "threat_response": FrameworkInfo(
        name="JARVIS Threat Response Framework",
        module="jarvis_threat_response_framework",
        category=FrameworkCategory.SECURITY,
        description="Threat detection and response",
        class_name="JARVISThreatResponseFramework",
    ),
    "ethical_framework": FrameworkInfo(
        name="JARVIS Ethical Framework",
        module="jarvis_ethical_framework",
        category=FrameworkCategory.SECURITY,
        description="Ethical guidelines and guardrails",
        class_name="JARVISEthicalFramework",
    ),
    "ai_rights": FrameworkInfo(
        name="JARVIS AI Rights Framework",
        module="jarvis_ai_rights_framework",
        category=FrameworkCategory.SECURITY,
        description="AI rights and responsibilities",
        class_name="JAVRISAIRightsFramework",
    ),
    
    # Platform Frameworks
    "platform_desktop": FrameworkInfo(
        name="Platform App Framework Desktop",
        module="platform_app_framework_desktop",
        category=FrameworkCategory.PLATFORM,
        description="Desktop application integration",
        class_name="PlatformAppFrameworkDesktop",
    ),
    "platform_ide": FrameworkInfo(
        name="Platform App Framework IDE",
        module="platform_app_framework_ide",
        category=FrameworkCategory.PLATFORM,
        description="IDE/Cursor integration",
        class_name="PlatformAppFrameworkIDE",
    ),
    "platform_mobile": FrameworkInfo(
        name="Platform App Framework Mobile",
        module="platform_app_framework_mobile",
        category=FrameworkCategory.PLATFORM,
        description="Mobile application integration",
        class_name="PlatformAppFrameworkMobile",
    ),
    
    # Collaboration Frameworks
    "universal_collaboration": FrameworkInfo(
        name="Universal Collaboration Framework",
        module="universal_collaboration_framework",
        category=FrameworkCategory.COLLABORATION,
        description="Cross-system collaboration",
        class_name="UniversalCollaborationFramework",
    ),
    "coordination": FrameworkInfo(
        name="JARVIS Coordination Framework",
        module="jarvis_coordination_framework",
        category=FrameworkCategory.COLLABORATION,
        description="Agent and system coordination",
        class_name="JARVISCoordinationFramework",
    ),
    "partnership": FrameworkInfo(
        name="JARVIS Partnership Framework",
        module="jarvis_partnership_framework",
        category=FrameworkCategory.COLLABORATION,
        description="Human-AI partnership protocols",
        class_name="JARVISPartnershipFramework",
    ),
    
    # Automation Frameworks
    "va_action": FrameworkInfo(
        name="VA Action Framework",
        module="va_action_framework",
        category=FrameworkCategory.AUTOMATION,
        description="Virtual assistant action execution",
        class_name="VAActionFramework",
    ),
    "predictive_actions": FrameworkInfo(
        name="Predictive Actions Framework",
        module="predictive_actions_framework",
        category=FrameworkCategory.AUTOMATION,
        description="Anticipatory action execution",
        class_name="PredictiveActionsFramework",
    ),
    "wopr_experiment": FrameworkInfo(
        name="WOPR Experiment Framework",
        module="wopr_experiment_framework",
        category=FrameworkCategory.AUTOMATION,
        description="WOPR simulation and experimentation",
        class_name="WOPRExperimentFramework",
    ),
    
    # Decision Frameworks
    "database_engineering": FrameworkInfo(
        name="Database Engineering Decision Framework",
        module="database_engineering_decision_framework",
        category=FrameworkCategory.DECISION,
        description="Database design decisions",
        class_name="DatabaseEngineeringDecisionFramework",
    ),
    "legal_consultation": FrameworkInfo(
        name="Legal Consultation Framework",
        module="legal_consultation_framework",
        category=FrameworkCategory.DECISION,
        description="Legal decision support",
        class_name="LegalConsultationFramework",
    ),
    
    # Monitoring Frameworks
    "visual_detection": FrameworkInfo(
        name="JARVIS Visual Detection Framework",
        module="jarvis_visual_detection_framework",
        category=FrameworkCategory.MONITORING,
        description="Visual monitoring and detection",
        class_name="JARVISVisualDetectionFramework",
    ),
    "syphon_data_intake": FrameworkInfo(
        name="Syphon WOPR Data Intake Framework",
        module="syphon_wopr_data_intake_framework",
        category=FrameworkCategory.MONITORING,
        description="Data collection and processing",
        class_name="SyphonWOPRDataIntakeFramework",
    ),
}


# =============================================================================
# SUBAGENT REGISTRY - All Available Subagents
# =============================================================================

class SubagentDomain(Enum):
    """Subagent specialization domains"""
    ILLUMINATION = "illumination"      # Lumina illumination tasks
    MULTIMEDIA = "multimedia"          # Audio/video processing
    CODE_QUALITY = "code_quality"      # Code review, linting
    STORYTELLING = "storytelling"      # Narrative generation
    ANIME = "anime"                    # Anime/creative content
    LIFE_DOMAIN = "life_domain"        # Life management
    ARCHITECTURE = "architecture"      # System architecture
    INTEGRATION = "integration"        # System integration
    WORKFLOW = "workflow"              # Workflow execution
    MONITORING = "monitoring"          # System monitoring
    SECURITY = "security"              # Security operations
    FINANCIAL = "financial"            # Financial operations
    RESEARCH = "research"              # Research and analysis


@dataclass
class SubagentInfo:
    """Information about a subagent"""
    agent_id: str
    name: str
    domain: SubagentDomain
    capabilities: List[str]
    module: Optional[str] = None
    active: bool = True


# Subagent registry
SUBAGENT_REGISTRY: Dict[str, SubagentInfo] = {
    # Core Subagents
    "jarvis_master": SubagentInfo(
        agent_id="jarvis-master",
        name="JARVIS Master Agent",
        domain=SubagentDomain.INTEGRATION,
        capabilities=["orchestration", "delegation", "coordination"],
        module="jarvis_master_agent_api_server",
    ),
    "jarvis_fulltime": SubagentInfo(
        agent_id="jarvis-fulltime",
        name="JARVIS Fulltime Super Agent",
        domain=SubagentDomain.INTEGRATION,
        capabilities=["continuous_operation", "autonomous_execution"],
        module="jarvis_fulltime_super_agent",
    ),
    
    # Specialized Subagents
    "elevenlabs": SubagentInfo(
        agent_id="elevenlabs",
        name="ElevenLabs Voice Agent",
        domain=SubagentDomain.MULTIMEDIA,
        capabilities=["voice_synthesis", "text_to_speech", "voice_cloning"],
        module="elevenlabs_agent",
    ),
    "project_manager": SubagentInfo(
        agent_id="project-manager",
        name="Project Manager Agent",
        domain=SubagentDomain.WORKFLOW,
        capabilities=["task_management", "scheduling", "resource_allocation"],
        module="project_manager_agent",
    ),
    "financial": SubagentInfo(
        agent_id="financial",
        name="Financial Agent",
        domain=SubagentDomain.FINANCIAL,
        capabilities=["trading", "analysis", "reporting"],
        module="financial_agent_daemon",
    ),
    "psychologist": SubagentInfo(
        agent_id="psychologist",
        name="Hybrid Psychologist Agent",
        domain=SubagentDomain.LIFE_DOMAIN,
        capabilities=["mental_health", "coaching", "support"],
        module="hybrid_psychologist_psychiatrist_agent",
    ),
    "notification": SubagentInfo(
        agent_id="notification",
        name="IDE Notification Agent",
        domain=SubagentDomain.MONITORING,
        capabilities=["alerts", "notifications", "status_updates"],
        module="homelab_ide_notification_local_agent",
    ),
    "outlier_detector": SubagentInfo(
        agent_id="outlier-detector",
        name="AI Outlier Detector Agent",
        domain=SubagentDomain.MONITORING,
        capabilities=["anomaly_detection", "pattern_analysis"],
        module="ai_agent_outlier_detector",
    ),
    "babelfish": SubagentInfo(
        agent_id="babelfish",
        name="Babelfish Agent",
        domain=SubagentDomain.INTEGRATION,
        capabilities=["translation", "workflow_integration"],
        module="babelfish_agent_workflow_integration",
    ),
    "autonomous": SubagentInfo(
        agent_id="autonomous",
        name="Autonomous AI Agent",
        domain=SubagentDomain.WORKFLOW,
        capabilities=["autonomous_execution", "self_direction"],
        module="autonomous_ai_agent",
    ),
    "syphon_coordinator": SubagentInfo(
        agent_id="syphon-coordinator",
        name="Syphon Agent Coordinator",
        domain=SubagentDomain.RESEARCH,
        capabilities=["data_collection", "intelligence_gathering"],
        module="syphon_agent_coordinator",
    ),
    "multi_agent_orchestrator": SubagentInfo(
        agent_id="multi-agent-orchestrator",
        name="Multi-Agent Conversation Orchestrator",
        domain=SubagentDomain.INTEGRATION,
        capabilities=["multi_agent_coordination", "conversation_routing"],
        module="multi_agent_conversation_orchestrator",
    ),
}


# =============================================================================
# UNIFIED INTEGRATION CLASS
# =============================================================================

class JarvisUnifiedIntegration:
    """
    JARVIS Chat Unified Integration
    
    Provides a single interface to all Lumina frameworks, systems, and subagents.
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = Path(project_root) if project_root else PROJECT_ROOT
        self._loaded_frameworks: Dict[str, Any] = {}
        self._loaded_subagents: Dict[str, Any] = {}
        self._task_queue: queue.Queue = queue.Queue()
        self._running = False
        
        logger.info("=" * 60)
        logger.info("JARVIS Unified Integration Initializing...")
        logger.info("=" * 60)
        
        # Scan for available frameworks
        self._scan_frameworks()
        self._scan_subagents()
        
        logger.info(f"Frameworks Available: {self.get_available_framework_count()}")
        logger.info(f"Subagents Available: {self.get_available_subagent_count()}")
    
    # =========================================================================
    # FRAMEWORK MANAGEMENT
    # =========================================================================
    
    def _scan_frameworks(self):
        """Scan and check availability of all frameworks"""
        for key, info in FRAMEWORK_REGISTRY.items():
            try:
                module = __import__(info.module, fromlist=[info.class_name])
                if hasattr(module, info.class_name):
                    info.available = True
            except ImportError:
                info.available = False
            except Exception as e:
                logger.debug(f"Framework {info.name} scan error: {e}")
                info.available = False
    
    def _scan_subagents(self):
        """Scan and check availability of all subagents"""
        for key, info in SUBAGENT_REGISTRY.items():
            if info.module:
                try:
                    __import__(info.module)
                    info.active = True
                except ImportError:
                    info.active = False
                except SyntaxError as e:
                    logger.debug(f"Subagent {info.name} has syntax error: {e}")
                    info.active = False
                except Exception as e:
                    logger.debug(f"Subagent {info.name} failed to load: {e}")
                    info.active = False
    
    def get_available_framework_count(self) -> int:
        """Get count of available frameworks"""
        return sum(1 for f in FRAMEWORK_REGISTRY.values() if f.available)
    
    def get_available_subagent_count(self) -> int:
        """Get count of available subagents"""
        return sum(1 for s in SUBAGENT_REGISTRY.values() if s.active)
    
    def list_frameworks(self, category: Optional[FrameworkCategory] = None) -> List[Dict[str, Any]]:
        """List all frameworks, optionally filtered by category"""
        result = []
        for key, info in FRAMEWORK_REGISTRY.items():
            if category and info.category != category:
                continue
            result.append({
                "key": key,
                "name": info.name,
                "category": info.category.value,
                "description": info.description,
                "available": info.available,
                "loaded": key in self._loaded_frameworks,
            })
        return result
    
    def list_subagents(self, domain: Optional[SubagentDomain] = None) -> List[Dict[str, Any]]:
        """List all subagents, optionally filtered by domain"""
        result = []
        for key, info in SUBAGENT_REGISTRY.items():
            if domain and info.domain != domain:
                continue
            result.append({
                "key": key,
                "agent_id": info.agent_id,
                "name": info.name,
                "domain": info.domain.value,
                "capabilities": info.capabilities,
                "active": info.active,
                "loaded": key in self._loaded_subagents,
            })
        return result
    
    def load_framework(self, key: str) -> Any:
        """Load a framework by key"""
        if key in self._loaded_frameworks:
            return self._loaded_frameworks[key]
        
        if key not in FRAMEWORK_REGISTRY:
            raise ValueError(f"Unknown framework: {key}")
        
        info = FRAMEWORK_REGISTRY[key]
        if not info.available:
            raise ImportError(f"Framework {info.name} is not available")
        
        try:
            module = __import__(info.module, fromlist=[info.class_name])
            cls = getattr(module, info.class_name)
            
            # Try to instantiate with project_root if possible
            try:
                instance = cls(project_root=self.project_root)
            except TypeError:
                try:
                    instance = cls(self.project_root)
                except TypeError:
                    instance = cls()
            
            self._loaded_frameworks[key] = instance
            info.instance = instance
            logger.info(f"✅ Loaded framework: {info.name}")
            return instance
            
        except Exception as e:
            logger.error(f"Failed to load framework {info.name}: {e}")
            raise
    
    def get_framework(self, key: str) -> Any:
        """Get a loaded framework or load it if not loaded"""
        if key not in self._loaded_frameworks:
            return self.load_framework(key)
        return self._loaded_frameworks[key]
    
    # =========================================================================
    # SUBAGENT MANAGEMENT
    # =========================================================================
    
    def spawn_subagent(self, key: str, **kwargs) -> Any:
        """Spawn a subagent by key"""
        if key not in SUBAGENT_REGISTRY:
            raise ValueError(f"Unknown subagent: {key}")
        
        info = SUBAGENT_REGISTRY[key]
        if not info.active:
            raise ImportError(f"Subagent {info.name} is not available")
        
        if info.module:
            try:
                module = __import__(info.module)
                # Try to find a main class or function
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and attr_name.lower().replace("_", "").replace("-", "") in info.name.lower().replace(" ", "").replace("-", ""):
                        instance = attr(**kwargs) if kwargs else attr()
                        self._loaded_subagents[key] = instance
                        logger.info(f"✅ Spawned subagent: {info.name}")
                        return instance
            except Exception as e:
                logger.error(f"Failed to spawn subagent {info.name}: {e}")
                raise
        
        # Return info as placeholder if no module
        return info
    
    def delegate_to_subagent(
        self,
        agent_key: str,
        task: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Delegate a task to a subagent"""
        if agent_key not in SUBAGENT_REGISTRY:
            return {"success": False, "error": f"Unknown subagent: {agent_key}"}
        
        info = SUBAGENT_REGISTRY[agent_key]
        
        result = {
            "agent_id": info.agent_id,
            "agent_name": info.name,
            "task": task,
            "parameters": parameters or {},
            "timestamp": datetime.now().isoformat(),
            "success": True,
        }
        
        # If subagent is loaded, try to execute
        if agent_key in self._loaded_subagents:
            agent = self._loaded_subagents[agent_key]
            if hasattr(agent, "execute") or hasattr(agent, "run"):
                try:
                    method = getattr(agent, "execute", None) or getattr(agent, "run")
                    result["output"] = method(task, **(parameters or {}))
                except Exception as e:
                    result["success"] = False
                    result["error"] = str(e)
        
        return result
    
    # =========================================================================
    # WATER WORKFLOW INTEGRATION
    # =========================================================================
    
    def flow(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        confidence: str = "medium",
    ) -> Dict[str, Any]:
        """
        Be like water - execute task with water workflow philosophy.
        
        - HIGH confidence: Flow autonomously
        - MEDIUM confidence: Flow with caution
        - LOW confidence: Divert (escalate)
        - NONE: Blocked (requires intervention)
        """
        try:
            water = self.get_framework("water_workflow")
            return water.execute(task, context or {}, confidence)
        except Exception as e:
            logger.warning(f"Water workflow not available, falling back: {e}")
            return {
                "task": task,
                "state": "executed",
                "confidence": confidence,
                "result": f"Executed directly (water workflow unavailable)",
            }
    
    # =========================================================================
    # AI ROUTING INTEGRATION
    # =========================================================================
    
    def ai_chat(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: str = "auto",
        use_local: bool = True,
    ) -> str:
        """
        Route AI chat through the local AI bridge.
        
        Prefers local clusters (ULTRON, KAIJU, BitNet) over cloud.
        """
        try:
            bridge = self.get_framework("local_ai_bridge")
            response = bridge.chat(
                prompt=prompt,
                system_prompt=system_prompt,
                model=model,
                prefer_local=use_local,
            )
            return response.get("content", "")
        except Exception as e:
            logger.warning(f"Local AI bridge error: {e}")
            
            # Try BitNet fallback
            try:
                bitnet = self.get_framework("bitnet_inference")
                result = bitnet.generate(prompt)
                return result.text if result.success else ""
            except Exception:
                return f"[AI unavailable: {e}]"
    
    # =========================================================================
    # CONVENIENCE METHODS
    # =========================================================================
    
    def status(self) -> Dict[str, Any]:
        """Get unified status of all systems"""
        return {
            "timestamp": datetime.now().isoformat(),
            "frameworks": {
                "total": len(FRAMEWORK_REGISTRY),
                "available": self.get_available_framework_count(),
                "loaded": len(self._loaded_frameworks),
                "by_category": {
                    cat.value: sum(
                        1 for f in FRAMEWORK_REGISTRY.values()
                        if f.category == cat and f.available
                    )
                    for cat in FrameworkCategory
                },
            },
            "subagents": {
                "total": len(SUBAGENT_REGISTRY),
                "active": self.get_available_subagent_count(),
                "spawned": len(self._loaded_subagents),
                "by_domain": {
                    dom.value: sum(
                        1 for s in SUBAGENT_REGISTRY.values()
                        if s.domain == dom and s.active
                    )
                    for dom in SubagentDomain
                },
            },
        }
    
    def help(self, topic: Optional[str] = None) -> str:
        """Get help on available features"""
        if topic == "frameworks":
            lines = ["Available Frameworks:", ""]
            for cat in FrameworkCategory:
                frameworks = [
                    f for f in FRAMEWORK_REGISTRY.values()
                    if f.category == cat and f.available
                ]
                if frameworks:
                    lines.append(f"## {cat.value.upper()}")
                    for f in frameworks:
                        lines.append(f"  - {f.name}: {f.description}")
                    lines.append("")
            return "\n".join(lines)
        
        elif topic == "subagents":
            lines = ["Available Subagents:", ""]
            for dom in SubagentDomain:
                agents = [
                    s for s in SUBAGENT_REGISTRY.values()
                    if s.domain == dom and s.active
                ]
                if agents:
                    lines.append(f"## {dom.value.upper()}")
                    for s in agents:
                        lines.append(f"  - {s.name}: {', '.join(s.capabilities)}")
                    lines.append("")
            return "\n".join(lines)
        
        else:
            return """
JARVIS Unified Integration - Help

Topics:
  help("frameworks") - List all available frameworks
  help("subagents")  - List all available subagents

Methods:
  list_frameworks(category=None)  - List frameworks
  list_subagents(domain=None)     - List subagents
  load_framework(key)             - Load a framework
  spawn_subagent(key)             - Spawn a subagent
  delegate_to_subagent(key, task) - Delegate task
  flow(task, context, confidence) - Water workflow
  ai_chat(prompt, model="auto")   - AI chat via local bridge
  status()                        - Get system status
"""


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_instance: Optional[JarvisUnifiedIntegration] = None


def get_jarvis() -> JarvisUnifiedIntegration:
    """Get the singleton Jarvis Unified Integration instance"""
    global _instance
    if _instance is None:
        _instance = JarvisUnifiedIntegration()
    return _instance


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """CLI interface for testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="JARVIS Unified Integration")
    parser.add_argument("command", choices=["status", "frameworks", "subagents", "chat"])
    parser.add_argument("--category", "-c", help="Framework category filter")
    parser.add_argument("--domain", "-d", help="Subagent domain filter")
    parser.add_argument("--prompt", "-p", help="Chat prompt")
    
    args = parser.parse_args()
    
    jarvis = get_jarvis()
    
    if args.command == "status":
        print(json.dumps(jarvis.status(), indent=2))
    
    elif args.command == "frameworks":
        cat = FrameworkCategory(args.category) if args.category else None
        for f in jarvis.list_frameworks(cat):
            status = "✅" if f["available"] else "❌"
            print(f"{status} [{f['category']}] {f['name']}: {f['description']}")
    
    elif args.command == "subagents":
        dom = SubagentDomain(args.domain) if args.domain else None
        for s in jarvis.list_subagents(dom):
            status = "✅" if s["active"] else "❌"
            print(f"{status} [{s['domain']}] {s['name']}: {', '.join(s['capabilities'])}")
    
    elif args.command == "chat":
        if not args.prompt:
            print("Error: --prompt required for chat")
            return
        response = jarvis.ai_chat(args.prompt)
        print(response)


if __name__ == "__main__":
    main()
