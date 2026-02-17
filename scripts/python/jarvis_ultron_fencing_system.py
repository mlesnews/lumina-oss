#!/usr/bin/env python3
"""
JARVIS ULTRON Fencing System

Implements cluster fencing for ULTRON hybrid cluster with intelligent
troubleshooting and decision-making via AIQ and JEDI-COUNCIL.

Fencing: Isolating misbehaving nodes to prevent cluster corruption.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISULTRONFencing")

try:
    from jarvis_ultron_hybrid_cluster import ULTRONHybridCluster, ClusterNode
    CLUSTER_AVAILABLE = True
except ImportError:
    CLUSTER_AVAILABLE = False
    logger.error("ULTRON Hybrid Cluster not available")

try:
    from universal_decision_tree import decide, DecisionContext, DecisionOutcome
    DECISION_TREE_AVAILABLE = True
except ImportError:
    DECISION_TREE_AVAILABLE = False
    logger.warning("Universal Decision Tree not available")


class FenceState(Enum):
    """Fence states for cluster nodes"""
    HEALTHY = "healthy"  # Node is healthy and operational
    DEGRADED = "degraded"  # Node showing issues but still usable
    FENCED = "fenced"  # Node is fenced (isolated)
    RECOVERING = "recovering"  # Node is recovering from fence
    FAILED = "failed"  # Node has failed permanently


class FenceReason(Enum):
    """Reasons for fencing a node"""
    HEALTH_CHECK_FAILED = "health_check_failed"
    RESPONSE_TIME_EXCEEDED = "response_time_exceeded"
    ERROR_RATE_EXCEEDED = "error_rate_exceeded"
    CONSECUTIVE_FAILURES = "consecutive_failures"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    MANUAL_FENCE = "manual_fence"
    TROUBLESHOOTING = "troubleshooting"  # Fenced for investigation


class ULTRONFencingSystem:
    """
    ULTRON Fencing System

    Implements intelligent fencing with:
    - AIQ decision-making
    - JEDI-COUNCIL consultation
    - Troubleshooting integration
    - Automatic recovery
    """

    def __init__(self, project_root: Path, cluster: Optional[ULTRONHybridCluster] = None):
        self.project_root = project_root
        self.logger = logger

        # Cluster reference
        if cluster:
            self.cluster = cluster
        elif CLUSTER_AVAILABLE:
            self.cluster = ULTRONHybridCluster(project_root)
        else:
            self.cluster = None
            self.logger.error("❌ ULTRON Cluster not available")

        # Fencing configuration
        self.config = self._load_config()

        # Fence states for each node
        self.fence_states: Dict[ClusterNode, FenceState] = {
            node: FenceState.HEALTHY for node in ClusterNode
        }

        # Fence history
        self.fence_history: List[Dict[str, Any]] = []

        # Node metrics for decision-making
        self.node_metrics: Dict[ClusterNode, Dict[str, Any]] = {
            node: {
                "consecutive_failures": 0,
                "error_rate": 0.0,
                "avg_response_time": 0.0,
                "last_success": None,
                "last_failure": None,
                "fence_count": 0
            }
            for node in ClusterNode
        }

        # AIQ Integration
        self.aiq_integration = None
        self._init_aiq_integration()

        # JEDI-COUNCIL Integration
        self.jedi_council_integration = None
        self._init_jedi_council_integration()

        self.logger.info("✅ ULTRON Fencing System initialized")

    def _load_config(self) -> Dict[str, Any]:
        """Load fencing configuration"""
        config_file = self.project_root / "config" / "ultron_fencing_config.json"

        default_config = {
            "fencing_enabled": True,
            "auto_fence": True,
            "auto_recovery": True,
            "fence_thresholds": {
                "consecutive_failures": 3,
                "error_rate": 0.5,  # 50% error rate
                "response_time_ms": 10000,  # 10 seconds
                "health_check_failures": 5
            },
            "recovery_thresholds": {
                "consecutive_successes": 3,
                "health_check_successes": 3
            },
            "fence_duration_minutes": 5,  # Minimum time before recovery attempt
            "aiq_decision_required": True,
            "jedi_council_consultation": True,
            "troubleshooting_enabled": True
        }

        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                self.logger.warning(f"⚠️  Failed to load config: {e}, using defaults")
        else:
            # Save default config
            try:
                config_file.parent.mkdir(parents=True, exist_ok=True)
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2)
            except Exception as e:
                self.logger.warning(f"⚠️  Failed to save default config: {e}")

        return default_config

    def _init_aiq_integration(self):
        """Initialize AIQ integration for decision-making"""
        try:
            from master_feedback_loop_aiq_integration import MasterFeedbackLoopAIQIntegration
            self.aiq_integration = MasterFeedbackLoopAIQIntegration()
            self.logger.info("✅ AIQ Integration initialized")
        except ImportError:
            self.logger.debug("AIQ Integration not available")
        except Exception as e:
            self.logger.debug(f"AIQ Integration error: {e}")

    def _consult_jedi_council(self, decision_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Consult JEDI-COUNCIL for high-level decisions

        Uses #JEDI-COUNCIL and #JEDI-HIGH-COUNCIL for cluster decisions.
        """
        # JEDI-COUNCIL consultation logic
        # In production, would integrate with actual JEDI-COUNCIL system

        decision_type = decision_context.get("action", "unknown")

        if decision_type == "fence_node":
            # High-level decision: Should we fence this node?
            return {
                "recommendation": "fence",
                "confidence": 0.9,
                "reasoning": "Node showing consistent failures, fencing recommended",
                "council": "JEDI-HIGH-COUNCIL"
            }
        elif decision_type == "unfence_node":
            # High-level decision: Is node ready for recovery?
            return {
                "recommendation": "unfence",
                "confidence": 0.8,
                "reasoning": "Node health restored, ready for recovery",
                "council": "JEDI-COUNCIL"
            }

        return {
            "recommendation": "consult",
            "confidence": 0.5,
            "reasoning": "Requires further analysis",
            "council": "JEDI-COUNCIL"
        }

    def _init_jedi_council_integration(self):
        """Initialize JEDI-COUNCIL integration"""
        try:
            # JEDI-COUNCIL integration would go here
            # For now, placeholder
            self.logger.debug("JEDI-COUNCIL Integration placeholder")
        except Exception as e:
            self.logger.debug(f"JEDI-COUNCIL Integration error: {e}")

    def evaluate_node_health(self, node: ClusterNode) -> Dict[str, Any]:
        """
        Evaluate node health and determine if fencing is needed

        Uses AIQ and JEDI-COUNCIL for intelligent decision-making.
        """
        if not self.cluster:
            return {"error": "Cluster not available"}

        node_config = self.cluster.nodes[node]
        metrics = self.node_metrics[node]
        current_state = self.fence_states[node]

        # Gather health data
        health_data = {
            "node": node.value,
            "node_name": node_config["name"],
            "current_state": current_state.value,
            "health": node_config["health"],
            "response_time": node_config["response_time"],
            "load": node_config["load"],
            "consecutive_failures": metrics["consecutive_failures"],
            "error_rate": metrics["error_rate"],
            "last_success": metrics["last_success"].isoformat() if metrics["last_success"] else None,
            "last_failure": metrics["last_failure"].isoformat() if metrics["last_failure"] else None
        }

        # Decision context for AIQ
        decision_context = {
            "action": "evaluate_node_fencing",
            "node": node.value,
            "health_data": health_data,
            "thresholds": self.config["fence_thresholds"],
            "current_state": current_state.value
        }

        # Use Universal Decision Tree for #DECISIONING
        if DECISION_TREE_AVAILABLE:
            try:
                decision_context_obj = DecisionContext(
                    action="evaluate_node_fencing",
                    context=health_data,
                    tags=["#TROUBLESHOOTING", "#DECISIONING", "@AIQ"]
                )
                decision = decide("cluster_node_health", decision_context_obj)
                health_data["decision_tree_outcome"] = decision.outcome.value if decision else None
                health_data["decision_tree_reasoning"] = decision.reasoning if decision else None
            except Exception as e:
                self.logger.debug(f"Decision tree error: {e}")

        # Use AIQ for decision-making if available
        if self.aiq_integration:
            try:
                aiq_decision = self.aiq_integration.analyze_decision_context(decision_context)
                health_data["aiq_recommendation"] = aiq_decision
            except Exception as e:
                self.logger.debug(f"AIQ decision error: {e}")

        # Evaluate fencing criteria
        should_fence = False
        fence_reason = None

        if not node_config["health"]:
            if metrics["consecutive_failures"] >= self.config["fence_thresholds"]["consecutive_failures"]:
                should_fence = True
                fence_reason = FenceReason.CONSECUTIVE_FAILURES
            elif metrics["consecutive_failures"] >= self.config["fence_thresholds"]["health_check_failures"]:
                should_fence = True
                fence_reason = FenceReason.HEALTH_CHECK_FAILED

        if metrics["error_rate"] >= self.config["fence_thresholds"]["error_rate"]:
            should_fence = True
            fence_reason = FenceReason.ERROR_RATE_EXCEEDED

        if node_config["response_time"] * 1000 >= self.config["fence_thresholds"]["response_time_ms"]:
            should_fence = True
            fence_reason = FenceReason.RESPONSE_TIME_EXCEEDED

        health_data["should_fence"] = should_fence
        health_data["fence_reason"] = fence_reason.value if fence_reason else None

        return health_data

    def fence_node(self, node: ClusterNode, reason: FenceReason, 
                  troubleshooting: bool = False) -> Dict[str, Any]:
        """
        Fence (isolate) a cluster node

        Args:
            node: Node to fence
            reason: Reason for fencing
            troubleshooting: If True, fence for troubleshooting/investigation
        """
        if not self.cluster:
            return {"success": False, "error": "Cluster not available"}

        current_state = self.fence_states[node]

        if current_state == FenceState.FENCED:
            self.logger.warning(f"⚠️  Node {node.value} is already fenced")
            return {"success": False, "error": "Node already fenced"}

        # Consult JEDI-COUNCIL if enabled (#JEDI-COUNCIL, #JEDI-HIGH-COUNCIL)
        if self.config.get("jedi_council_consultation", True):
            self.logger.info(f"🏛️  Consulting JEDI-COUNCIL for fencing decision: {node.value}")
            jedi_decision = self._consult_jedi_council(decision_context)
            self.logger.info(f"   JEDI-COUNCIL Recommendation: {jedi_decision.get('recommendation')} (Confidence: {jedi_decision.get('confidence', 0):.2f})")

            # Use Universal Decision Tree for #DECISIONING
            if DECISION_TREE_AVAILABLE:
                try:
                    decision_context_obj = DecisionContext(
                        action="fence_node",
                        context=decision_context,
                        tags=["#TROUBLESHOOTING", "#DECISIONING", "@AIQ", "#JEDI-COUNCIL"]
                    )
                    decision = decide("cluster_fencing", decision_context_obj)
                    if decision:
                        self.logger.info(f"   Decision Tree: {decision.outcome.value} - {decision.reasoning}")
                except Exception as e:
                    self.logger.debug(f"Decision tree error: {e}")

        # Use AIQ for decision-making
        if self.config.get("aiq_decision_required", True) and self.aiq_integration:
            decision_context = {
                "action": "fence_node",
                "node": node.value,
                "reason": reason.value,
                "troubleshooting": troubleshooting,
                "current_state": current_state.value
            }
            try:
                aiq_decision = self.aiq_integration.analyze_decision_context(decision_context)
                self.logger.info(f"🧠 AIQ Decision: {aiq_decision}")
            except Exception as e:
                self.logger.debug(f"AIQ decision error: {e}")

        # Perform fencing
        self.fence_states[node] = FenceState.FENCED
        self.cluster.nodes[node]["enabled"] = False
        metrics = self.node_metrics[node]
        metrics["fence_count"] += 1

        # Record fence event
        fence_event = {
            "timestamp": datetime.now().isoformat(),
            "node": node.value,
            "node_name": self.cluster.nodes[node]["name"],
            "reason": reason.value,
            "troubleshooting": troubleshooting,
            "previous_state": current_state.value,
            "fence_count": metrics["fence_count"]
        }

        self.fence_history.append(fence_event)

        self.logger.warning(f"🔒 FENCED: {self.cluster.nodes[node]['name']} ({reason.value})")

        # Start troubleshooting if enabled
        if troubleshooting and self.config.get("troubleshooting_enabled", True):
            self._start_troubleshooting(node, reason)

        return {
            "success": True,
            "node": node.value,
            "reason": reason.value,
            "fence_event": fence_event
        }

    def unfence_node(self, node: ClusterNode) -> Dict[str, Any]:
        """Unfence (restore) a cluster node"""
        if not self.cluster:
            return {"success": False, "error": "Cluster not available"}

        current_state = self.fence_states[node]

        if current_state != FenceState.FENCED:
            self.logger.warning(f"⚠️  Node {node.value} is not fenced (state: {current_state.value})")
            return {"success": False, "error": f"Node not fenced (state: {current_state.value})"}

        # Check if node is healthy
        self.cluster._check_node_health(node)
        node_config = self.cluster.nodes[node]

        if not node_config["health"]:
            self.logger.warning(f"⚠️  Cannot unfence {node.value}: node is still unhealthy")
            self.fence_states[node] = FenceState.RECOVERING
            return {"success": False, "error": "Node still unhealthy"}

        # Unfence
        self.fence_states[node] = FenceState.HEALTHY
        self.cluster.nodes[node]["enabled"] = True
        metrics = self.node_metrics[node]
        metrics["consecutive_failures"] = 0
        metrics["error_rate"] = 0.0

        self.logger.info(f"✅ UNFENCED: {self.cluster.nodes[node]['name']}")

        return {
            "success": True,
            "node": node.value,
            "state": "healthy"
        }

    def _start_troubleshooting(self, node: ClusterNode, reason: FenceReason):
        """Start troubleshooting process for fenced node"""
        self.logger.info(f"🔧 Starting troubleshooting for {self.cluster.nodes[node]['name']}...")

        # Troubleshooting steps
        troubleshooting_steps = [
            "Check network connectivity",
            "Verify service is running",
            "Check system resources (CPU, memory, disk)",
            "Review error logs",
            "Test endpoint accessibility",
            "Verify configuration"
        ]

        # Record troubleshooting
        troubleshooting_event = {
            "timestamp": datetime.now().isoformat(),
            "node": node.value,
            "reason": reason.value,
            "steps": troubleshooting_steps,
            "status": "in_progress"
        }

        self.logger.info(f"   Troubleshooting steps: {', '.join(troubleshooting_steps)}")

        # In production, would execute actual troubleshooting
        return troubleshooting_event

    def monitor_and_fence(self) -> Dict[str, Any]:
        """
        Monitor all nodes and fence if needed

        This is the main monitoring loop that uses AIQ and JEDI-COUNCIL
        for intelligent decision-making.
        """
        if not self.cluster:
            return {"error": "Cluster not available"}

        results = {
            "timestamp": datetime.now().isoformat(),
            "nodes_evaluated": 0,
            "nodes_fenced": 0,
            "nodes_unfenced": 0,
            "evaluations": []
        }

        for node in ClusterNode:
            # Skip if already fenced (unless checking for recovery)
            if self.fence_states[node] == FenceState.FENCED:
                # Check if ready for recovery
                if self.config.get("auto_recovery", True):
                    recovery_result = self._check_recovery(node)
                    if recovery_result.get("ready"):
                        unfence_result = self.unfence_node(node)
                        if unfence_result["success"]:
                            results["nodes_unfenced"] += 1
                continue

            # Evaluate node health
            evaluation = self.evaluate_node_health(node)
            results["evaluations"].append(evaluation)
            results["nodes_evaluated"] += 1

            # Update metrics
            self._update_metrics(node, evaluation)

            # Fence if needed
            if evaluation.get("should_fence") and self.config.get("auto_fence", True):
                reason = FenceReason(evaluation["fence_reason"])
                fence_result = self.fence_node(node, reason, troubleshooting=True)
                if fence_result["success"]:
                    results["nodes_fenced"] += 1

        return results

    def _update_metrics(self, node: ClusterNode, evaluation: Dict[str, Any]):
        """Update node metrics based on evaluation"""
        metrics = self.node_metrics[node]

        if evaluation.get("health"):
            metrics["consecutive_failures"] = 0
            metrics["last_success"] = datetime.now()
        else:
            metrics["consecutive_failures"] += 1
            metrics["last_failure"] = datetime.now()

        # Update error rate (simplified)
        if metrics["consecutive_failures"] > 0:
            metrics["error_rate"] = min(1.0, metrics["consecutive_failures"] / 10.0)
        else:
            metrics["error_rate"] = 0.0

        # Update response time
        if evaluation.get("response_time"):
            metrics["avg_response_time"] = evaluation["response_time"]

    def _check_recovery(self, node: ClusterNode) -> Dict[str, Any]:
        """Check if fenced node is ready for recovery"""
        # Check health
        self.cluster._check_node_health(node)
        node_config = self.cluster.nodes[node]

        if node_config["health"]:
            # Check recovery thresholds
            metrics = self.node_metrics[node]
            # Simplified: if healthy, ready for recovery
            return {"ready": True, "node": node.value}

        return {"ready": False, "node": node.value}

    def get_fencing_status(self) -> Dict[str, Any]:
        """Get current fencing status"""
        return {
            "fencing_enabled": self.config.get("fencing_enabled", True),
            "nodes": {
                node.value: {
                    "state": self.fence_states[node].value,
                    "metrics": self.node_metrics[node].copy(),
                    "fence_count": self.node_metrics[node]["fence_count"]
                }
                for node in ClusterNode
            },
            "fence_history_count": len(self.fence_history),
            "recent_fences": self.fence_history[-5:] if self.fence_history else []
        }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="ULTRON Fencing System")
        parser.add_argument("--monitor", action="store_true", help="Monitor and fence nodes")
        parser.add_argument("--status", action="store_true", help="Get fencing status")
        parser.add_argument("--fence", type=str, choices=["ultron_local", "kaiju_iron_legion"], 
                           help="Manually fence a node")
        parser.add_argument("--unfence", type=str, choices=["ultron_local", "kaiju_iron_legion"],
                           help="Unfence a node")
        parser.add_argument("--evaluate", type=str, choices=["ultron_local", "kaiju_iron_legion"],
                           help="Evaluate node health")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        fencing = ULTRONFencingSystem(project_root)

        if args.monitor:
            results = fencing.monitor_and_fence()
            import json
            print(json.dumps(results, indent=2, default=str))

        elif args.status:
            status = fencing.get_fencing_status()
            import json
            print(json.dumps(status, indent=2, default=str))

        elif args.fence:
            node = ClusterNode(args.fence)
            result = fencing.fence_node(node, FenceReason.MANUAL_FENCE)
            print(json.dumps(result, indent=2, default=str))

        elif args.unfence:
            node = ClusterNode(args.unfence)
            result = fencing.unfence_node(node)
            print(json.dumps(result, indent=2, default=str))

        elif args.evaluate:
            node = ClusterNode(args.evaluate)
            evaluation = fencing.evaluate_node_health(node)
            import json
            print(json.dumps(evaluation, indent=2, default=str))

        else:
            print("Usage:")
            print("  --monitor          : Monitor and fence nodes")
            print("  --status           : Get fencing status")
            print("  --fence <node>     : Manually fence a node")
            print("  --unfence <node>   : Unfence a node")
            print("  --evaluate <node>  : Evaluate node health")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()