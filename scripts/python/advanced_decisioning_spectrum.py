#!/usr/bin/env python3
"""
Advanced Decisioning Spectrum System

Implements a 9-model approval system across three tiers:
- Local AI (ULTRON/Iron Legion)
- Free Cloud AI (GitHub Models)
- Premium Cloud AI (Claude/GPT/Gemini)

Decisioning levels from self-approval to 9-model consensus for critical decisions.

Tags: #DECISIONING #SPECTRUM #9_MODEL_APPROVAL #WOPR @LUMINA
"""

import sys
import json
import time
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    logger = get_logger("DecisioningSpectrum")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.get_logger("DecisioningSpectrum")


class DecisionTier(Enum):
    """Decision approval tiers"""
    SELF_APPROVAL = "self_approval"          # Single model, automatic
    LOCAL_CONSENSUS = "local_consensus"      # 3 local models
    HYBRID_APPROVAL = "hybrid_approval"      # Local + Free cloud (5 models)
    FULL_CONSENSUS = "full_consensus"        # All 9 models across all tiers


class DecisionCriticality(Enum):
    """Decision criticality levels"""
    LOW = "low"           # Self-approval
    MEDIUM = "medium"     # Local consensus
    HIGH = "high"         # Hybrid approval
    CRITICAL = "critical" # Full 9-model consensus


class DecisioningSpectrum:
    """
    Advanced decisioning spectrum with 9-model approval system:

    Tier 1 - Local AI (3 models):
    - ULTRON (qwen2.5:72b) - Primary local model
    - Iron Legion (distributed nodes) - Specialized models
    - Kaiju (qwen2.5:14b) - Fast local model

    Tier 2 - Free Cloud AI (3 models):
    - GitHub Models (various) - Free tier
    - Alternative free providers

    Tier 3 - Premium Cloud AI (3 models):
    - Claude (Anthropic)
    - GPT (OpenAI)
    - Gemini (Google)

    Total: 9 models across 3 tiers for maximum consensus
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.active_decisions = {}
        self.decision_history = []
        self.approval_matrix = self._initialize_approval_matrix()
        self.consensus_thresholds = self._initialize_consensus_thresholds()

        # Model configurations for each tier
        self.tier_models = self._initialize_tier_models()

        logger.info("🎯 Advanced Decisioning Spectrum initialized with 9-model approval system")

    def _initialize_approval_matrix(self) -> Dict[str, Dict[str, Any]]:
        """Initialize the decision approval matrix"""
        return {
            DecisionCriticality.LOW.value: {
                "tier": DecisionTier.SELF_APPROVAL.value,
                "required_models": 1,
                "consensus_threshold": 1.0,  # 100% agreement (just itself)
                "max_processing_time": 5,  # seconds
                "auto_approve": True,
                "description": "Self-approval for routine decisions"
            },
            DecisionCriticality.MEDIUM.value: {
                "tier": DecisionTier.LOCAL_CONSENSUS.value,
                "required_models": 3,
                "consensus_threshold": 0.67,  # 2/3 agreement
                "max_processing_time": 30,
                "auto_approve": False,
                "description": "Local consensus for important decisions"
            },
            DecisionCriticality.HIGH.value: {
                "tier": DecisionTier.HYBRID_APPROVAL.value,
                "required_models": 5,
                "consensus_threshold": 0.8,  # 4/5 agreement
                "max_processing_time": 120,
                "auto_approve": False,
                "description": "Hybrid approval for significant decisions"
            },
            DecisionCriticality.CRITICAL.value: {
                "tier": DecisionTier.FULL_CONSENSUS.value,
                "required_models": 9,
                "consensus_threshold": 0.89,  # 8/9 agreement
                "max_processing_time": 300,  # 5 minutes
                "auto_approve": False,
                "description": "Full 9-model consensus for mission-critical decisions"
            }
        }

    def _initialize_consensus_thresholds(self) -> Dict[str, float]:
        """Initialize consensus thresholds for different decision types"""
        return {
            "code_deployment": 0.8,
            "security_changes": 0.9,
            "financial_decisions": 0.95,
            "system_configuration": 0.75,
            "user_interface_changes": 0.6,
            "documentation_updates": 0.5,
            "routine_maintenance": 0.3
        }

    def _initialize_tier_models(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize models for each approval tier"""
        return {
            "local": [
                {
                    "name": "ULTRON",
                    "model": "qwen2.5:72b",
                    "endpoint": "http://<NAS_IP>:8080",
                    "provider": "ollama",
                    "cost_per_token": 0.0,
                    "max_tokens": 32768,
                    "specialization": "general_intelligence"
                },
                {
                    "name": "Iron_Legion_Primary",
                    "model": "qwen2.5:14b",
                    "endpoint": "http://<NAS_PRIMARY_IP>:3001",
                    "provider": "ollama",
                    "cost_per_token": 0.0,
                    "max_tokens": 8192,
                    "specialization": "combat_analysis"
                },
                {
                    "name": "Kaiju",
                    "model": "qwen2.5:14b",
                    "endpoint": "http://<NAS_PRIMARY_IP>:11434",
                    "provider": "ollama",
                    "cost_per_token": 0.0,
                    "max_tokens": 8192,
                    "specialization": "fast_processing"
                }
            ],
            "free_cloud": [
                {
                    "name": "GitHub_Copilot",
                    "model": "gpt-4o-mini",
                    "endpoint": "https://api.github.com/copilot",
                    "provider": "github",
                    "cost_per_token": 0.0,  # Free tier
                    "max_tokens": 128000,
                    "specialization": "code_assistance"
                },
                {
                    "name": "GitHub_Models_Secondary",
                    "model": "claude-3-haiku",
                    "endpoint": "https://api.github.com/models",
                    "provider": "github",
                    "cost_per_token": 0.0,
                    "max_tokens": 200000,
                    "specialization": "analysis"
                },
                {
                    "name": "HuggingFace_Free",
                    "model": "microsoft/DialoGPT-medium",
                    "endpoint": "https://api-inference.huggingface.co/models",
                    "provider": "huggingface",
                    "cost_per_token": 0.0,
                    "max_tokens": 1024,
                    "specialization": "conversation"
                }
            ],
            "premium_cloud": [
                {
                    "name": "Claude_3_Opus",
                    "model": "claude-3-opus-20240229",
                    "endpoint": "https://api.anthropic.com",
                    "provider": "anthropic",
                    "cost_per_token": 0.00015,
                    "max_tokens": 200000,
                    "specialization": "deep_reasoning"
                },
                {
                    "name": "GPT_4_Turbo",
                    "model": "gpt-4-turbo-preview",
                    "endpoint": "https://api.openai.com",
                    "provider": "openai",
                    "cost_per_token": 0.00001,
                    "max_tokens": 128000,
                    "specialization": "creative_problem_solving"
                },
                {
                    "name": "Gemini_1_5_Pro",
                    "model": "gemini-1.5-pro",
                    "endpoint": "https://generativelanguage.googleapis.com",
                    "provider": "google",
                    "cost_per_token": 0.0000025,
                    "max_tokens": 2097152,
                    "specialization": "multimodal_analysis"
                }
            ]
        }

    def evaluate_decision_criticality(self, decision_context: Dict[str, Any]) -> DecisionCriticality:
        """
        Evaluate decision criticality based on context

        Factors considered:
        - Financial impact
        - Security implications
        - User experience impact
        - System stability risk
        - Reversibility
        """

        # Extract decision factors
        financial_impact = decision_context.get("financial_impact", 0)
        security_risk = decision_context.get("security_risk", 0)
        user_impact = decision_context.get("user_impact", 0)
        system_risk = decision_context.get("system_risk", 0)
        reversibility = decision_context.get("reversibility", 1.0)  # 1.0 = fully reversible

        # Calculate criticality score (0-1)
        criticality_score = (
            financial_impact * 0.3 +
            security_risk * 0.3 +
            user_impact * 0.2 +
            system_risk * 0.15 +
            (1 - reversibility) * 0.05  # Lower reversibility increases criticality
        )

        # Determine criticality level
        if criticality_score < 0.2:
            return DecisionCriticality.LOW
        elif criticality_score < 0.5:
            return DecisionCriticality.MEDIUM
        elif criticality_score < 0.8:
            return DecisionCriticality.HIGH
        else:
            return DecisionCriticality.CRITICAL

    def submit_decision_for_approval(self, decision_id: str, decision_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit a decision for approval through the spectrum

        Args:
            decision_id: Unique identifier for the decision
            decision_context: Context including decision details and factors

        Returns:
            Decision submission result with approval tier and requirements
        """

        # Evaluate criticality
        criticality = self.evaluate_decision_criticality(decision_context)

        # Get approval requirements
        approval_config = self.approval_matrix[criticality.value]

        # Create decision record
        decision_record = {
            "decision_id": decision_id,
            "context": decision_context,
            "criticality": criticality.value,
            "approval_tier": approval_config["tier"],
            "required_models": approval_config["required_models"],
            "consensus_threshold": approval_config["consensus_threshold"],
            "max_processing_time": approval_config["max_processing_time"],
            "submitted_at": datetime.now().isoformat(),
            "status": "pending",
            "approvals": [],
            "rejections": [],
            "processing_start": None,
            "processing_end": None
        }

        # Store decision
        self.active_decisions[decision_id] = decision_record

        # Auto-approve if configured
        if approval_config["auto_approve"]:
            decision_record["status"] = "approved"
            decision_record["approved_at"] = datetime.now().isoformat()
            decision_record["approval_method"] = "auto_approval"
            logger.info(f"✅ Decision {decision_id} auto-approved (criticality: {criticality.value})")
        else:
            # Start approval process
            threading.Thread(
                target=self._process_decision_approval,
                args=(decision_id,),
                daemon=True
            ).start()

            logger.info(f"🎯 Decision {decision_id} submitted for {approval_config['tier']} approval ({approval_config['required_models']} models required)")

        return {
            "decision_id": decision_id,
            "criticality": criticality.value,
            "approval_tier": approval_config["tier"],
            "required_models": approval_config["required_models"],
            "estimated_completion": approval_config["max_processing_time"],
            "status": decision_record["status"]
        }

    def _process_decision_approval(self, decision_id: str):
        """Process decision approval through the appropriate tier"""
        if decision_id not in self.active_decisions:
            logger.error(f"Decision {decision_id} not found")
            return

        decision = self.active_decisions[decision_id]
        decision["processing_start"] = datetime.now().isoformat()

        approval_config = self.approval_matrix[decision["criticality"]]
        tier = approval_config["tier"]

        logger.info(f"🚀 Starting {tier} approval process for decision {decision_id}")

        # Execute approval based on tier
        if tier == DecisionTier.SELF_APPROVAL.value:
            result = self._execute_self_approval(decision)
        elif tier == DecisionTier.LOCAL_CONSENSUS.value:
            result = self._execute_local_consensus(decision)
        elif tier == DecisionTier.HYBRID_APPROVAL.value:
            result = self._execute_hybrid_approval(decision)
        elif tier == DecisionTier.FULL_CONSENSUS.value:
            result = self._execute_full_consensus(decision)
        else:
            result = {"approved": False, "reason": "Unknown approval tier"}

        # Update decision record
        decision["processing_end"] = datetime.now().isoformat()
        decision["result"] = result
        decision["status"] = "approved" if result["approved"] else "rejected"

        # Move to history
        self.decision_history.append(decision)
        del self.active_decisions[decision_id]

        logger.info(f"✅ Decision {decision_id} completed: {'APPROVED' if result['approved'] else 'REJECTED'}")

    def _execute_self_approval(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Execute self-approval (single model)"""
        # Simple confidence check
        confidence = self._assess_decision_confidence(decision["context"])

        return {
            "approved": confidence >= 0.8,
            "confidence": confidence,
            "approving_models": ["ULTRON"],
            "reason": "Self-approval based on confidence assessment"
        }

    def _execute_local_consensus(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Execute local consensus (3 local models)"""
        return self._execute_tier_consensus(decision, ["local"], 3, 0.67)

    def _execute_hybrid_approval(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Execute hybrid approval (local + free cloud, 5 models)"""
        return self._execute_tier_consensus(decision, ["local", "free_cloud"], 5, 0.8)

    def _execute_full_consensus(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Execute full consensus (all 9 models across all tiers)"""
        return self._execute_tier_consensus(decision, ["local", "free_cloud", "premium_cloud"], 9, 0.89)

    def _execute_tier_consensus(self, decision: Dict[str, Any], tiers: List[str],
                               required_count: int, threshold: float) -> Dict[str, Any]:
        """Execute consensus across specified tiers"""

        all_approvals = []
        approving_models = []

        # Query models from each tier
        for tier in tiers:
            tier_models = self.tier_models[tier]

            for model_config in tier_models:
                try:
                    approval = self._query_model_approval(model_config, decision)
                    all_approvals.append(approval)

                    if approval["approved"]:
                        approving_models.append(model_config["name"])

                    # Break if we have enough approvals
                    approval_rate = sum(1 for a in all_approvals if a["approved"]) / len(all_approvals)
                    if approval_rate >= threshold and len([a for a in all_approvals if a["approved"]]) >= required_count:
                        break

                except Exception as e:
                    logger.warning(f"Model {model_config['name']} failed: {e}")
                    all_approvals.append({"approved": False, "error": str(e)})

            # Break if we have consensus
            if len(approving_models) >= required_count:
                break

        # Calculate final result
        total_approvals = len([a for a in all_approvals if a.get("approved", False)])
        approval_rate = total_approvals / len(all_approvals) if all_approvals else 0

        approved = approval_rate >= threshold and total_approvals >= required_count

        return {
            "approved": approved,
            "approval_rate": approval_rate,
            "total_approvals": total_approvals,
            "total_queries": len(all_approvals),
            "approving_models": approving_models,
            "required_count": required_count,
            "threshold": threshold,
            "reason": f"{'Approved' if approved else 'Rejected'} with {total_approvals}/{len(all_approvals)} model approvals"
        }

    def _query_model_approval(self, model_config: Dict[str, Any], decision: Dict[str, Any]) -> Dict[str, Any]:
        """Query a specific model for decision approval"""

        # Simulate model query (in real implementation, this would make actual API calls)
        model_name = model_config["name"]

        # Simulate processing time based on model and decision complexity
        processing_time = model_config.get("processing_time", 2) + decision["context"].get("complexity", 0) * 5

        # Simulate approval decision based on model characteristics
        base_confidence = 0.8
        if "premium" in model_config.get("provider", ""):
            base_confidence += 0.1  # Premium models are more conservative
        elif "free" in model_config.get("provider", ""):
            base_confidence -= 0.1  # Free models are more lenient

        # Add some randomness for realism
        import random
        confidence = base_confidence + (random.random() - 0.5) * 0.2
        confidence = max(0.1, min(0.9, confidence))

        # Decision based on confidence and decision context
        approved = confidence >= 0.6  # Simple threshold

        time.sleep(min(processing_time, 1))  # Simulate processing time

        return {
            "approved": approved,
            "confidence": confidence,
            "model": model_name,
            "processing_time": processing_time,
            "reason": f"{'Approved' if approved else 'Rejected'} with {confidence:.2f} confidence"
        }

    def _assess_decision_confidence(self, decision_context: Dict[str, Any]) -> float:
        """Assess overall decision confidence"""
        # Simple confidence calculation based on context factors
        base_confidence = 0.8

        # Adjust based on known factors
        if decision_context.get("well_analyzed", False):
            base_confidence += 0.1
        if decision_context.get("high_risk", False):
            base_confidence -= 0.2
        if decision_context.get("time_pressure", False):
            base_confidence -= 0.1

        return max(0.1, min(1.0, base_confidence))

    def get_decision_status(self, decision_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a decision"""
        if decision_id in self.active_decisions:
            return self.active_decisions[decision_id]

        # Check history
        for decision in self.decision_history[-100:]:  # Last 100 decisions
            if decision["decision_id"] == decision_id:
                return decision

        return None

    def get_spectrum_metrics(self) -> Dict[str, Any]:
        """Get comprehensive spectrum metrics"""
        total_decisions = len(self.decision_history) + len(self.active_decisions)
        approved_decisions = len([d for d in self.decision_history if d.get("status") == "approved"])

        approval_rate = approved_decisions / total_decisions if total_decisions > 0 else 0

        # Tier breakdown
        tier_stats = {}
        for decision in self.decision_history:
            tier = decision.get("approval_tier", "unknown")
            if tier not in tier_stats:
                tier_stats[tier] = {"total": 0, "approved": 0}
            tier_stats[tier]["total"] += 1
            if decision.get("status") == "approved":
                tier_stats[tier]["approved"] += 1

        return {
            "total_decisions_processed": total_decisions,
            "overall_approval_rate": approval_rate,
            "active_decisions": len(self.active_decisions),
            "tier_breakdown": tier_stats,
            "average_processing_time": self._calculate_average_processing_time(),
            "model_utilization": self._calculate_model_utilization()
        }

    def _calculate_average_processing_time(self) -> float:
        """Calculate average decision processing time"""
        processing_times = []
        for decision in self.decision_history:
            if decision.get("processing_start") and decision.get("processing_end"):
                start = datetime.fromisoformat(decision["processing_start"])
                end = datetime.fromisoformat(decision["processing_end"])
                processing_times.append((end - start).total_seconds())

        return sum(processing_times) / len(processing_times) if processing_times else 0

    def _calculate_model_utilization(self) -> Dict[str, int]:
        """Calculate model utilization across all decisions"""
        utilization = {}

        for decision in self.decision_history:
            result = decision.get("result", {})
            approving_models = result.get("approving_models", [])
            for model in approving_models:
                utilization[model] = utilization.get(model, 0) + 1

        return utilization


# Global instance
_decisioning_spectrum: Optional[DecisioningSpectrum] = None


def get_decisioning_spectrum() -> DecisioningSpectrum:
    """Get global decisioning spectrum instance"""
    global _decisioning_spectrum
    if _decisioning_spectrum is None:
        _decisioning_spectrum = DecisioningSpectrum(project_root)
    return _decisioning_spectrum


def submit_critical_decision(decision_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Submit a decision for approval through the 9-model spectrum"""
    spectrum = get_decisioning_spectrum()
    return spectrum.submit_decision_for_approval(decision_id, context)


def get_spectrum_status() -> Dict[str, Any]:
    """Get comprehensive spectrum status"""
    spectrum = get_decisioning_spectrum()
    return spectrum.get_spectrum_metrics()


if __name__ == "__main__":
    # Initialize the decisioning spectrum
    spectrum = get_decisioning_spectrum()

    # Example usage: Submit different types of decisions
    decisions = [
        {
            "decision_id": "deploy_minor_fix",
            "context": {
                "type": "code_deployment",
                "financial_impact": 0.1,
                "security_risk": 0.0,
                "user_impact": 0.2,
                "system_risk": 0.1,
                "reversibility": 0.9,
                "description": "Deploy minor bug fix"
            }
        },
        {
            "decision_id": "security_patch",
            "context": {
                "type": "security_changes",
                "financial_impact": 0.3,
                "security_risk": 0.8,
                "user_impact": 0.1,
                "system_risk": 0.4,
                "reversibility": 0.7,
                "description": "Deploy critical security patch"
            }
        },
        {
            "decision_id": "system_rearchitecture",
            "context": {
                "type": "system_configuration",
                "financial_impact": 0.9,
                "security_risk": 0.6,
                "user_impact": 0.8,
                "system_risk": 0.9,
                "reversibility": 0.2,
                "description": "Complete system rearchitecture"
            }
        }
    ]

    print("🎯 Testing 9-Model Decisioning Spectrum")
    print("=" * 50)

    for decision in decisions:
        result = submit_critical_decision(decision["decision_id"], decision["context"])
        print(f"Decision: {decision['decision_id']}")
        print(f"  Criticality: {result['criticality']}")
        print(f"  Approval Tier: {result['approval_tier']}")
        print(f"  Required Models: {result['required_models']}")
        print(f"  Status: {result['status']}")
        print()

    # Wait for processing
    time.sleep(5)

    # Get final status
    status = get_spectrum_status()
    print("📊 Final Spectrum Status:")
    print(f"  Total Decisions: {status['total_decisions_processed']}")
    print(f"  Approval Rate: {status['overall_approval_rate']:.1%}")
    print(f"  Average Processing Time: {status['average_processing_time']:.1f}s")
    print(f"  Active Decisions: {status['active_decisions']}")

    print("\n🎯 9-Model Decisioning Spectrum Ready!")
    print("   - Self-approval for routine decisions")
    print("   - Local consensus (3 models) for important decisions")
    print("   - Hybrid approval (5 models) for significant decisions")
    print("   - Full consensus (9 models) for critical decisions")