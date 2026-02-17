#!/usr/bin/env python3
"""
LUMINA Decisioning Engine - ENHANCED with ULTRON AUTO Parallel Execution
                    -LUM THE MODERN

Enhanced with:
- ULTRON AUTO parallel execution logic
- Smart routing (ADAPT, IMPROVISE, OVERCOME)
- Integration with ULTRON Unified Cluster
- Warp Factor control

@LUMINA @JARVIS @ULTRON @DECISIONING -LUM_THE_MODERN
"""

import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("DecisioningEngineEnhanced")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("DecisioningEngineEnhanced")

# Import ULTRON AUTO parallel execution
try:
    from scripts.python.ultron_auto_parallel import (
        ULTRONAutoParallel,
        ExecutionMode,
        AutoDecision
    )
    ULTRON_AUTO_AVAILABLE = True
except ImportError:
    ULTRON_AUTO_AVAILABLE = False
    logger.warning("⚠️  ULTRON AUTO not available")

# Import Warp Factor Controller
try:
    from scripts.python.ultron_warp_factor_controller import (
        ULTRONWarpFactorController,
        WarpFactor
    )
    WARP_FACTOR_AVAILABLE = True
except ImportError:
    WARP_FACTOR_AVAILABLE = False
    logger.warning("⚠️  Warp Factor Controller not available")

# Import base decisioning engine
try:
    from scripts.python.lumina_decisioning_engine import (
        LuminaDecisioningEngine,
        DecisionContext,
        DecisionAction
    )
    BASE_DECISIONING_AVAILABLE = True
except ImportError:
    BASE_DECISIONING_AVAILABLE = False
    logger.warning("⚠️  Base decisioning engine not available")


class AIDecisionContext(Enum):
    """AI-specific decision contexts"""
    MODEL_ROUTING = "model_routing"           # Which model to use
    PARALLEL_EXECUTION = "parallel_execution" # Should run parallel?
    COST_OPTIMIZATION = "cost_optimization"   # Cost vs quality tradeoff
    QUALITY_REQUIREMENT = "quality_requirement" # Quality threshold needed


class AIDecisionAction(Enum):
    """AI-specific decision actions"""
    USE_LOCAL_ONLY = "use_local_only"
    USE_CLOUD_ONLY = "use_cloud_only"
    USE_PARALLEL = "use_parallel"
    USE_SUBSCRIPTION = "use_subscription"
    USE_HYBRID = "use_hybrid"


class LuminaDecisioningEngineEnhanced(LuminaDecisioningEngine):
    """
    Enhanced Decisioning Engine with ULTRON AUTO parallel execution.

    Integrates:
    - ULTRON AUTO parallel execution logic
    - Warp Factor control
    - Smart routing (ADAPT, IMPROVISE, OVERCOME)
    - Cost optimization
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize enhanced decisioning engine"""
        super().__init__(project_root)

        # Initialize ULTRON AUTO
        self.ultron_auto = None
        if ULTRON_AUTO_AVAILABLE:
            try:
                self.ultron_auto = ULTRONAutoParallel()
                logger.info("✅ ULTRON AUTO parallel execution integrated")
            except Exception as e:
                logger.warning(f"⚠️  ULTRON AUTO init error: {e}")

        # Initialize Warp Factor Controller
        self.warp_controller = None
        if WARP_FACTOR_AVAILABLE:
            try:
                self.warp_controller = ULTRONWarpFactorController()
                logger.info("✅ Warp Factor Controller integrated")
            except Exception as e:
                logger.warning(f"⚠️  Warp Factor Controller init error: {e}")

        logger.info("=" * 80)
        logger.info("🚀 LUMINA DECISIONING ENGINE - ENHANCED")
        logger.info("                    -LUM THE MODERN")
        logger.info("=" * 80)
        logger.info("   Features:")
        logger.info("   • ULTRON AUTO parallel execution")
        logger.info("   • Warp Factor control")
        logger.info("   • Smart routing (ADAPT, IMPROVISE, OVERCOME)")
        logger.info("   • Cost optimization")
        logger.info("=" * 80)

    def decide_ai_routing(
        self,
        prompt: str,
        context_tokens: int = 0,
        task_type: Optional[str] = None,
        require_frontier: bool = False,
        cost_sensitive: bool = True
    ) -> Dict[str, Any]:
        """
        #DECISIONING: Decide AI routing strategy.

        ADAPT: Analyzes request complexity
        IMPROVISE: Decides if parallel execution is beneficial
        OVERCOME: Returns routing decision with reasoning
        """
        logger.info(f"🤔 #DECISIONING: AI Routing Decision")
        logger.info(f"   Prompt length: {len(prompt)} chars")
        logger.info(f"   Context tokens: {context_tokens}")
        logger.info(f"   Task type: {task_type or 'auto'}")

        # Get current warp factor
        current_warp = WarpFactor.WARP_9  # Default
        if self.warp_controller:
            current_warp = self.warp_controller.current_warp

        # ADAPT: Analyze request using ULTRON AUTO
        auto_decision = None
        if self.ultron_auto:
            auto_decision = self.ultron_auto.analyze_request(
                prompt=prompt,
                context_tokens=context_tokens,
                task_type=task_type
            )
        else:
            # Fallback analysis
            auto_decision = AutoDecision(
                mode=ExecutionMode.LOCAL_ONLY,
                reasoning="ULTRON AUTO not available - defaulting to local",
                should_parallel=False,
                local_model="mistral:latest",
                cloud_model=None,
                estimated_cost=0.0
            )

        # IMPROVISE: Check warp factor constraints
        if self.warp_controller:
            warp_config = self.warp_controller.configs[current_warp]

            # Override parallel decision based on warp factor
            if not warp_config.use_parallel:
                if auto_decision.should_parallel:
                    auto_decision.should_parallel = False
                    auto_decision.mode = ExecutionMode.LOCAL_ONLY
                    auto_decision.reasoning += " (Warp factor disables parallel)"

            # Check cloud request limits
            if warp_config.max_cloud_requests_per_day:
                # Would need to track daily usage - placeholder
                pass

        # OVERCOME: Build final decision
        decision = {
            "timestamp": datetime.now().isoformat(),
            "decision_type": "ai_routing",
            "warp_factor": current_warp.value,
            "warp_name": current_warp.name,
            "execution_mode": auto_decision.mode.value,
            "should_parallel": auto_decision.should_parallel,
            "local_model": auto_decision.local_model,
            "cloud_model": auto_decision.cloud_model,
            "estimated_cost": auto_decision.estimated_cost,
            "reasoning": auto_decision.reasoning,
            "confidence": 0.9,
            "alternative_options": [
                {
                    "option": "local_only",
                    "cost": 0.0,
                    "quality": "good",
                    "latency": "low"
                },
                {
                    "option": "parallel",
                    "cost": auto_decision.estimated_cost,
                    "quality": "excellent",
                    "latency": "medium"
                }
            ]
        }

        # Log decision
        logger.info(f"   ✅ Decision: {auto_decision.mode.value}")
        logger.info(f"   Reasoning: {auto_decision.reasoning}")
        if auto_decision.should_parallel:
            logger.info(f"   ⚡ PARALLEL EXECUTION: Local + Cloud")

        return decision

    def decide_parallel_execution(
        self,
        prompt: str,
        complexity_score: float = 0.5,
        quality_requirement: float = 0.7
    ) -> Dict[str, Any]:
        """
        #DECISIONING: Decide if parallel execution is beneficial.

        Factors:
        - Request complexity
        - Quality requirement
        - Cost sensitivity
        - Warp factor setting
        """
        logger.info(f"🤔 #DECISIONING: Parallel Execution Decision")

        # Get warp factor
        current_warp = WarpFactor.WARP_9
        if self.warp_controller:
            current_warp = self.warp_controller.current_warp
            warp_config = self.warp_controller.configs[current_warp]

            if not warp_config.use_parallel:
                return {
                    "should_parallel": False,
                    "reasoning": f"Warp {current_warp.value} disables parallel execution",
                    "warp_factor": current_warp.value
                }

        # Analyze if parallel is beneficial
        should_parallel = False
        reasoning = ""

        # High complexity → Parallel beneficial
        if complexity_score > 0.7:
            should_parallel = True
            reasoning = "High complexity - Parallel execution provides best results"

        # High quality requirement → Parallel beneficial
        elif quality_requirement > 0.9:
            should_parallel = True
            reasoning = "High quality requirement - Parallel execution ensures best quality"

        # Long prompt → Parallel beneficial
        elif len(prompt) > 500:
            should_parallel = True
            reasoning = "Complex prompt - Parallel execution for speed + quality"

        else:
            should_parallel = False
            reasoning = "Simple task - Single route sufficient"

        decision = {
            "should_parallel": should_parallel,
            "reasoning": reasoning,
            "complexity_score": complexity_score,
            "quality_requirement": quality_requirement,
            "warp_factor": current_warp.value
        }

        logger.info(f"   ✅ Parallel: {should_parallel}")
        logger.info(f"   Reasoning: {reasoning}")

        return decision

    def decide_cost_optimization(
        self,
        estimated_local_cost: float,
        estimated_cloud_cost: float,
        quality_difference: float = 0.1
    ) -> Dict[str, Any]:
        """
        #DECISIONING: Optimize cost vs quality tradeoff.

        Considers:
        - Cost difference
        - Quality difference
        - Warp factor budget
        """
        logger.info(f"🤔 #DECISIONING: Cost Optimization")

        # Get warp factor budget
        current_warp = WarpFactor.WARP_9
        monthly_budget = 100.0
        if self.warp_controller:
            current_warp = self.warp_controller.current_warp
            monthly_budget = self.warp_controller.configs[current_warp].estimated_monthly_cost

        # Calculate cost per request (rough estimate)
        daily_budget = monthly_budget / 30
        request_budget = daily_budget / 100  # Assume 100 requests/day

        # Decision logic
        if estimated_cloud_cost > request_budget:
            decision = {
                "use_cloud": False,
                "reasoning": f"Cloud cost ${estimated_cloud_cost:.4f} exceeds budget ${request_budget:.4f}",
                "recommendation": "use_local"
            }
        elif quality_difference < 0.1:
            decision = {
                "use_cloud": False,
                "reasoning": f"Quality difference {quality_difference:.2f} too small to justify cloud cost",
                "recommendation": "use_local"
            }
        else:
            decision = {
                "use_cloud": True,
                "reasoning": f"Quality difference {quality_difference:.2f} justifies cloud cost ${estimated_cloud_cost:.4f}",
                "recommendation": "use_cloud"
            }

        logger.info(f"   ✅ Recommendation: {decision['recommendation']}")
        logger.info(f"   Reasoning: {decision['reasoning']}")

        return decision

    def make_ai_decision(
        self,
        prompt: str,
        context: Dict[str, Any],
        user_preference: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        #DECISIONING: Comprehensive AI decision-making.

        Integrates all decision factors:
        - Routing (local/cloud/parallel)
        - Cost optimization
        - Quality requirements
        - Warp factor constraints
        """
        logger.info("=" * 80)
        logger.info("🤔 #DECISIONING: Comprehensive AI Decision")
        logger.info("=" * 80)

        # Extract context
        context_tokens = context.get("context_tokens", 0)
        task_type = context.get("task_type")
        require_frontier = context.get("require_frontier", False)
        cost_sensitive = context.get("cost_sensitive", True)
        complexity_score = context.get("complexity_score", 0.5)
        quality_requirement = context.get("quality_requirement", 0.7)

        # Step 1: Routing decision
        routing_decision = self.decide_ai_routing(
            prompt=prompt,
            context_tokens=context_tokens,
            task_type=task_type,
            require_frontier=require_frontier,
            cost_sensitive=cost_sensitive
        )

        # Step 2: Parallel execution decision
        parallel_decision = self.decide_parallel_execution(
            prompt=prompt,
            complexity_score=complexity_score,
            quality_requirement=quality_requirement
        )

        # Step 3: Cost optimization
        cost_decision = self.decide_cost_optimization(
            estimated_local_cost=0.0,
            estimated_cloud_cost=routing_decision.get("estimated_cost", 0.0),
            quality_difference=0.1
        )

        # Final decision synthesis
        final_decision = {
            "timestamp": datetime.now().isoformat(),
            "decision_type": "comprehensive_ai",
            "routing": routing_decision,
            "parallel": parallel_decision,
            "cost_optimization": cost_decision,
            "final_recommendation": self._synthesize_final_decision(
                routing_decision,
                parallel_decision,
                cost_decision
            ),
            "warp_factor": routing_decision.get("warp_factor", 9),
            "reasoning": self._build_comprehensive_reasoning(
                routing_decision,
                parallel_decision,
                cost_decision
            )
        }

        logger.info("=" * 80)
        logger.info(f"✅ FINAL DECISION: {final_decision['final_recommendation']}")
        logger.info("=" * 80)

        return final_decision

    def _synthesize_final_decision(
        self,
        routing: Dict[str, Any],
        parallel: Dict[str, Any],
        cost: Dict[str, Any]
    ) -> str:
        """Synthesize final decision from all factors"""
        if parallel.get("should_parallel") and routing.get("should_parallel"):
            return "use_parallel"
        elif cost.get("recommendation") == "use_cloud":
            return "use_cloud"
        else:
            return "use_local"

    def _build_comprehensive_reasoning(
        self,
        routing: Dict[str, Any],
        parallel: Dict[str, Any],
        cost: Dict[str, Any]
    ) -> str:
        """Build comprehensive reasoning from all decisions"""
        parts = [
            f"Routing: {routing.get('reasoning', 'N/A')}",
            f"Parallel: {parallel.get('reasoning', 'N/A')}",
            f"Cost: {cost.get('reasoning', 'N/A')}"
        ]
        return " | ".join(parts)


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="LUMINA Enhanced Decisioning Engine")
    parser.add_argument("--routing", type=str, help="Decide AI routing for prompt")
    parser.add_argument("--parallel", type=str, help="Decide parallel execution for prompt")
    parser.add_argument("--comprehensive", type=str, help="Comprehensive AI decision")
    parser.add_argument("--warp", type=int, help="Set warp factor (1-11)")

    args = parser.parse_args()

    engine = LuminaDecisioningEngineEnhanced()

    if args.warp:
        if engine.warp_controller:
            try:
                warp = WarpFactor(args.warp)
                engine.warp_controller.set_warp_factor(warp)
                engine.warp_controller.print_warp_status()
            except ValueError as e:
                print(f"❌ Error: {e}")
        else:
            print("❌ Warp Factor Controller not available")

    elif args.routing:
        decision = engine.decide_ai_routing(args.routing)
        print(f"\n🎯 ROUTING DECISION:")
        print(f"   Mode: {decision['execution_mode']}")
        print(f"   Parallel: {decision['should_parallel']}")
        print(f"   Local Model: {decision['local_model']}")
        print(f"   Cloud Model: {decision['cloud_model'] or 'N/A'}")
        print(f"   Est. Cost: ${decision['estimated_cost']:.4f}")
        print(f"   Reasoning: {decision['reasoning']}")

    elif args.parallel:
        decision = engine.decide_parallel_execution(args.parallel)
        print(f"\n⚡ PARALLEL DECISION:")
        print(f"   Should Parallel: {decision['should_parallel']}")
        print(f"   Reasoning: {decision['reasoning']}")

    elif args.comprehensive:
        decision = engine.make_ai_decision(
            prompt=args.comprehensive,
            context={
                "context_tokens": 1000,
                "complexity_score": 0.7,
                "quality_requirement": 0.8
            }
        )
        print(f"\n🚀 COMPREHENSIVE DECISION:")
        print(f"   Final Recommendation: {decision['final_recommendation']}")
        print(f"   Warp Factor: {decision['warp_factor']}")
        print(f"   Reasoning: {decision['reasoning']}")

    else:
        print("\n🚀 LUMINA Enhanced Decisioning Engine")
        print("   Use --routing, --parallel, or --comprehensive with a prompt")
        print("   Use --warp <1-11> to set warp factor")


if __name__ == "__main__":


    main()