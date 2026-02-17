#!/usr/bin/env python3
"""
JARVIS Unified Interface - Production Ready

ONE INTERFACE - Works everywhere (workspace or non-workspace)
JARVIS delegates to all agents and company workers

"Can't you just do it for me? Can't I just have one interface and just work from there?"
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class InterfaceMode(Enum):
    """Interface modes - works everywhere"""
    UNIFIED = "unified"  # One interface, works everywhere
    WORKSPACE = "workspace"  # Workspace mode (if detected)
    NON_WORKSPACE = "non_workspace"  # Non-workspace mode (if detected)
    AUTO = "auto"  # Auto-detect and adapt


@dataclass
class DelegationTarget:
    """Target for JARVIS delegation"""
    agent_id: str
    agent_name: str
    agent_type: str  # "droid", "system", "service", "worker"
    capabilities: List[str]
    status: str = "available"
    location: str = "@helpdesk"  # Default location
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class JARVISUnifiedInterface:
    """
    JARVIS Unified Interface

    ONE INTERFACE - Works everywhere
    JARVIS delegates to all agents and company workers
    """

    def __init__(self, project_root: Optional[Path] = None, mode: InterfaceMode = InterfaceMode.AUTO):
        """Initialize unified interface"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("JARVISUnifiedInterface")
        self.mode = mode

        # Initialize Workflow Scope & Mode Orchestrator
        try:
            from workflow_scope_mode_orchestrator import WorkflowScopeModeOrchestrator
            self.scope_mode_orchestrator = WorkflowScopeModeOrchestrator(self.project_root)
            self.logger.info("   ✅ Workflow Scope & Mode Orchestrator integrated")
        except Exception as e:
            self.scope_mode_orchestrator = None
            self.logger.debug(f"   Scope/Mode orchestrator not available: {e}")

        # Auto-detect mode if needed
        if mode == InterfaceMode.AUTO:
            self.mode = self._detect_mode()

        # Delegation targets (all agents/workers)
        self.delegation_targets: Dict[str, DelegationTarget] = {}

        # Load all available agents/workers
        self._load_delegation_targets()

        # Initialize MANUS Auto-Grammarly
        try:
            from manus_auto_grammarly import MANUSAutoGrammarly
            self.auto_grammarly = MANUSAutoGrammarly()
            self.logger.info("   ✅ MANUS Auto-Grammarly enabled")
        except Exception as e:
            self.auto_grammarly = None
            self.logger.debug(f"   Auto-Grammarly not available: {e}")

        # Initialize AI Coordination
        try:
            from jarvis_ai_coordination import JARVISAICoordination
            self.ai_coordination = JARVISAICoordination(self.project_root)
            self.ai_coordination.sync_all_ais()  # Initial sync
            self.logger.info("   ✅ AI Coordination active - Stacking the deck")
        except Exception as e:
            self.ai_coordination = None
            self.logger.debug(f"   AI Coordination not available: {e}")

        # Initialize JARVIS Core Intelligence
        try:
            from jarvis_core_intelligence import JARVISCoreIntelligence
            self.core_intelligence = JARVISCoreIntelligence(self.project_root)
            self.logger.info("   ✅ Core Intelligence (MCU Feature) enabled")
        except Exception as e:
            self.core_intelligence = None
            self.logger.debug(f"   Core Intelligence not available: {e}")

        # Initialize MCU JARVIS Features
        try:
            from jarvis_home_automation import JARVISHomeAutomation
            self.home_automation = JARVISHomeAutomation(self.project_root)
            self.logger.info("   ✅ Home Automation (MCU Feature) enabled")
        except Exception as e:
            self.home_automation = None
            self.logger.debug(f"   Home Automation not available: {e}")

        try:
            from jarvis_security_surveillance import JARVISSecuritySurveillance
            self.security_surveillance = JARVISSecuritySurveillance(self.project_root)
            self.logger.info("   ✅ Security Surveillance (MCU Feature) enabled")
        except Exception as e:
            self.security_surveillance = None
            self.logger.debug(f"   Security Surveillance not available: {e}")

        try:
            from jarvis_proactive_monitoring import JARVISProactiveMonitoring
            self.proactive_monitoring = JARVISProactiveMonitoring(self.project_root)
            self.logger.info("   ✅ Proactive Monitoring (MCU Feature) enabled")
        except Exception as e:
            self.proactive_monitoring = None
            self.logger.debug(f"   Proactive Monitoring not available: {e}")

        self.logger.info("🎯 JARVIS Unified Interface initialized")
        self.logger.info(f"   Mode: {self.mode.value}")
        self.logger.info(f"   Works everywhere: YES")
        self.logger.info(f"   Delegation targets: {len(self.delegation_targets)}")

    def _detect_mode(self) -> InterfaceMode:
        try:
            """Auto-detect workspace vs non-workspace"""
            # Check if we're in a workspace
            workspace_indicators = [
                self.project_root / ".cursor",
                self.project_root / ".vscode",
                self.project_root / "workspace",
            ]

            if any(indicator.exists() for indicator in workspace_indicators):
                self.logger.info("   Detected: Workspace mode")
                return InterfaceMode.WORKSPACE
            else:
                self.logger.info("   Detected: Non-workspace mode")
                return InterfaceMode.NON_WORKSPACE

        except Exception as e:
            self.logger.error(f"Error in _detect_mode: {e}", exc_info=True)
            raise
    def _load_delegation_targets(self) -> None:
        """Load all available agents/workers for delegation"""
        # Droid Actor System
        try:
            from droid_actor_system import DroidActorSystem
            droid_system = DroidActorSystem(project_root=self.project_root)

            # Add all droids
            for droid_id, droid in droid_system.droids.items():
                self.delegation_targets[f"droid_{droid_id}"] = DelegationTarget(
                    agent_id=f"droid_{droid_id}",
                    agent_name=droid.name,
                    agent_type="droid",
                    capabilities=droid.expertise_areas,
                    location="@helpdesk",
                    metadata={"persona": droid.persona, "specialty": droid.specialty}
                )

            self.logger.info(f"   Loaded {len(droid_system.droids)} droids")
        except Exception as e:
            self.logger.debug(f"Could not load droid system: {e}")

        # JARVIS Helpdesk Integration
        try:
            from jarvis_helpdesk_integration import JARVISHelpdeskIntegration
            self.delegation_targets["jarvis_helpdesk"] = DelegationTarget(
                agent_id="jarvis_helpdesk",
                agent_name="JARVIS Helpdesk Integration",
                agent_type="system",
                capabilities=["workflow_verification", "droid_routing", "r5_ingestion", "escalation"],
                location="@helpdesk"
            )
        except Exception as e:
            self.logger.debug(f"Could not load JARVIS helpdesk: {e}")

        # R5 Living Context Matrix
        try:
            from r5_living_context_matrix import R5LivingContextMatrix
            self.delegation_targets["r5_matrix"] = DelegationTarget(
                agent_id="r5_matrix",
                agent_name="R5 Living Context Matrix",
                agent_type="system",
                capabilities=["knowledge_aggregation", "pattern_extraction", "context_management"],
                location="http://localhost:8000"
            )
        except Exception as e:
            self.logger.debug(f"Could not load R5: {e}")

        # Network Support Workflows
        try:
            from network_support_workflows import NetworkSupportWorkflows
            self.delegation_targets["network_support"] = DelegationTarget(
                agent_id="network_support",
                agent_name="Network Support Workflows",
                agent_type="service",
                capabilities=["network_diagnostics", "troubleshooting", "bau_workflows"],
                location="@network_support"
            )
        except Exception as e:
            self.logger.debug(f"Could not load network support: {e}")

        # NAS Service Monitor
        try:
            from nas_service_monitor import NASMasterCoordinator
            self.delegation_targets["nas_monitor"] = DelegationTarget(
                agent_id="nas_monitor",
                agent_name="NAS Service Monitor",
                agent_type="service",
                capabilities=["nas_monitoring", "health_checks", "service_coordination"],
                location="@nas"
            )
        except Exception as e:
            self.logger.debug(f"Could not load NAS monitor: {e}")

        # Symbiotic Cluster Coordinator
        try:
            from symbiotic_cluster_coordinator import SymbioticClusterCoordinator
            self.delegation_targets["symbiotic_cluster"] = DelegationTarget(
                agent_id="symbiotic_cluster",
                agent_name="Symbiotic Cluster Coordinator",
                agent_type="system",
                capabilities=["cluster_management", "load_balancing", "failover"],
                location="@iron_legion"
            )
        except Exception as e:
            self.logger.debug(f"Could not load symbiotic cluster: {e}")

        # AIOS Integration
        try:
            from jarvis_aios_integration import JARVISAIOSIntegration
            self.delegation_targets["aios_integration"] = DelegationTarget(
                agent_id="aios_integration",
                agent_name="AIOS Integration",
                agent_type="system",
                capabilities=["aios_integration", "icp_protocol", "web2_web3_hybrid", "trading_system"],
                location="@aios"
            )
        except Exception as e:
            self.logger.debug(f"Could not load AIOS integration: {e}")

        # Trading System (if available)
        try:
            from bitcoin_financial_workflows import BitcoinWorkflowSystem
            self.delegation_targets["trading_system"] = DelegationTarget(
                agent_id="trading_system",
                agent_name="Trading System",
                agent_type="service",
                capabilities=["trading", "portfolio_management", "risk_management"],
                location="@trading",
                status="in_progress"
            )
        except Exception as e:
            self.logger.debug(f"Could not load trading system: {e}")

    def delegate(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Delegate task to appropriate agent/worker

        JARVIS automatically selects the best agent for the task
        """
        # Auto-correct typos in task (MANUS Auto-Grammarly)
        if self.auto_grammarly:
            task = self.auto_grammarly.auto_correct_input(task)

        # Use Core Intelligence to understand intent (if available)
        intent = None
        if self.core_intelligence:
            intent = self.core_intelligence.understand_intent(task)
            self.logger.debug(f"   Intent detected: {intent.intent_type.value} (confidence: {intent.confidence:.2f})")

        # Analyze task to find best agent
        best_agent = self._select_agent(task, context)

        if not best_agent:
            return {
                "success": False,
                "error": "No suitable agent found",
                "task": task
            }

        self.logger.info(f"📋 Delegating to: {best_agent.agent_name} ({best_agent.agent_id})")

        # Execute delegation
        try:
            result = self._execute_delegation(best_agent, task, context)
            return {
                "success": True,
                "agent": best_agent.agent_id,
                "agent_name": best_agent.agent_name,
                "result": result,
                "task": task
            }
        except Exception as e:
            self.logger.error(f"Delegation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent": best_agent.agent_id,
                "task": task
            }

    def _select_agent(self, task: str, context: Optional[Dict[str, Any]] = None) -> Optional[DelegationTarget]:
        """Select best agent for task"""
        task_lower = task.lower()

        # Match task keywords to agent capabilities
        for agent_id, agent in self.delegation_targets.items():
            if agent.status != "available":
                continue

            # Check if agent capabilities match task
            for capability in agent.capabilities:
                if capability.lower() in task_lower or task_lower in capability.lower():
                    return agent

        # Default to C-3PO if available
        if "droid_c3po" in self.delegation_targets:
            return self.delegation_targets["droid_c3po"]

        # Default to JARVIS Helpdesk
        if "jarvis_helpdesk" in self.delegation_targets:
            return self.delegation_targets["jarvis_helpdesk"]

        return None

    def _execute_delegation(self, agent: DelegationTarget, task: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """Execute delegation to agent"""
        # Route to appropriate handler based on agent type
        if agent.agent_type == "droid":
            return self._delegate_to_droid(agent, task, context)
        elif agent.agent_type == "system":
            return self._delegate_to_system(agent, task, context)
        elif agent.agent_type == "service":
            return self._delegate_to_service(agent, task, context)
        else:
            return {"status": "delegated", "agent": agent.agent_id}

    def _delegate_to_droid(self, agent: DelegationTarget, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Delegate to droid"""
        droid_id = agent.agent_id.replace("droid_", "")

        try:
            from droid_actor_system import DroidActorSystem
            droid_system = DroidActorSystem(project_root=self.project_root)

            workflow_data = {
                "task": task,
                "context": context or {},
                "timestamp": datetime.now().isoformat()
            }

            # Use droid system to handle task
            verified, result = droid_system.verify_with_droid_actor(workflow_data)

            return {
                "droid": droid_id,
                "verified": verified,
                "result": result
            }
        except Exception as e:
            return {"error": str(e), "droid": droid_id}

    def _delegate_to_system(self, agent: DelegationTarget, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Delegate to system"""
        return {
            "system": agent.agent_id,
            "task": task,
            "status": "delegated",
            "message": f"Task delegated to {agent.agent_name}"
        }

    def _delegate_to_service(self, agent: DelegationTarget, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Delegate to service"""
        return {
            "service": agent.agent_id,
            "task": task,
            "status": "delegated",
            "message": f"Task delegated to {agent.agent_name}"
        }

    def get_status(self) -> Dict[str, Any]:
        """Get unified interface status"""
        status = {
            "mode": self.mode.value,
            "workspace_agnostic": True,
            "delegation_targets": len(self.delegation_targets),
            "available_agents": [
                {
                    "id": agent.agent_id,
                    "name": agent.agent_name,
                    "type": agent.agent_type,
                    "status": agent.status,
                    "capabilities": agent.capabilities
                }
                for agent in self.delegation_targets.values()
            ],
            "message": "ONE INTERFACE - Works everywhere. JARVIS delegates to all agents.",
            "mcu_features": {}
        }

        # Add MCU JARVIS feature status
        if self.home_automation:
            status["mcu_features"]["home_automation"] = self.home_automation.get_status_report()

        if self.security_surveillance:
            status["mcu_features"]["security_surveillance"] = self.security_surveillance.get_security_status()

        if self.proactive_monitoring:
            status["mcu_features"]["proactive_monitoring"] = self.proactive_monitoring.get_status_report()

        return status

    def list_agents(self) -> List[Dict[str, Any]]:
        """List all available agents/workers"""
        return [agent.to_dict() for agent in self.delegation_targets.values()]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Unified Interface")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--agents", action="store_true", help="List all agents")
    parser.add_argument("--delegate", type=str, help="Delegate task to agent")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    interface = JARVISUnifiedInterface()

    if args.status:
        status = interface.get_status()
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print("\n🎯 JARVIS Unified Interface Status")
            print("=" * 60)
            print(f"Mode: {status['mode']}")
            print(f"Workspace Agnostic: {status['workspace_agnostic']}")
            print(f"Delegation Targets: {status['delegation_targets']}")
            print(f"\n{status['message']}")
            print("\nAvailable Agents:")
            for agent in status['available_agents']:
                print(f"  • {agent['name']} ({agent['type']}) - {agent['status']}")

    elif args.agents:
        agents = interface.list_agents()
        if args.json:
            print(json.dumps(agents, indent=2))
        else:
            print("\n🤖 Available Agents/Workers")
            print("=" * 60)
            for agent in agents:
                print(f"\n{agent['agent_name']} ({agent['agent_id']})")
                print(f"  Type: {agent['agent_type']}")
                print(f"  Status: {agent['status']}")
                print(f"  Location: {agent['location']}")
                print(f"  Capabilities: {', '.join(agent['capabilities'])}")

    elif args.delegate:
        result = interface.delegate(args.delegate)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print("\n📋 Delegation Result")
            print("=" * 60)
            if result.get('success'):
                print(f"✅ Successfully delegated to: {result.get('agent_name')}")
                print(f"Agent: {result.get('agent')}")
            else:
                print(f"❌ Delegation failed: {result.get('error')}")

    else:
        parser.print_help()

