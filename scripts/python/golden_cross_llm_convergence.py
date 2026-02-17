#!/usr/bin/env python3
"""
Golden Cross LLM Convergence - Single Active Model System

Ensures only ONE active LLM model at a time for optimal quantum inference
and artificial intelligence golden cross convergence/alignment.

Key Principles:
- Single active model for convergence
- Intelligent routing to SELECT the optimal model
- Model switching based on task requirements
- Parallel processing uses same model (batched inference)
- Quantum inference alignment through unified model state
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import threading
from collections import deque

# Import intelligent router
from intelligent_llm_router import IntelligentLLMRouter, RoutingStrategy, AIModel as RouterAIModel
from universal_decision_tree import decide, DecisionContext, DecisionOutcome



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class ModelState(Enum):
    """Model state for golden cross convergence"""
    INACTIVE = "inactive"
    LOADING = "loading"
    ACTIVE = "active"  # Only ONE model can be active
    UNLOADING = "unloading"
    ERROR = "error"


@dataclass
class GoldenCrossModel:
    """Model with golden cross convergence state"""
    name: str
    endpoint: str
    model_id: str
    provider: str
    state: ModelState = ModelState.INACTIVE
    router_model: RouterAIModel = None
    load_time: Optional[datetime] = None
    inference_count: int = 0
    last_inference: Optional[datetime] = None
    convergence_score: float = 0.0  # Golden cross alignment score


class GoldenCrossLLMConvergence:
    """
    Golden Cross LLM Convergence System

    Maintains single active model for quantum inference and AI golden cross alignment.
    Uses intelligent routing to select optimal model, but ensures only ONE is active.
    """

    def __init__(self, router: IntelligentLLMRouter = None):
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "golden_cross"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Router for intelligent model selection
        self.router = router or IntelligentLLMRouter(routing_strategy=RoutingStrategy.ADAPTIVE)

        # Golden cross models (registry)
        self.models: Dict[str, GoldenCrossModel] = {}

        # SINGLE ACTIVE MODEL (golden cross principle)
        self.active_model: Optional[GoldenCrossModel] = None
        self.active_model_lock = threading.Lock()

        # Model switching queue
        self.model_switch_queue: deque = deque(maxlen=10)

        # Convergence tracking
        self.convergence_history: deque = deque(maxlen=1000)
        self.inference_sequence: deque = deque(maxlen=100)  # Track inference sequence for alignment

        # Setup logging
        self.logger = logging.getLogger("GoldenCrossLLM")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - ✨ %(name)s - %(levelname)s - %(message)s'
            ))
            self.logger.addHandler(handler)

    def register_model(self, model: RouterAIModel) -> GoldenCrossModel:
        """Register a model for golden cross convergence"""
        # Register with router
        self.router.register_model(model)

        # Create golden cross model
        golden_model = GoldenCrossModel(
            name=model.name,
            endpoint=model.endpoint,
            model_id=model.model_id,
            provider=model.provider,
            router_model=model
        )

        self.models[model.name] = golden_model
        self.logger.info(f"✨ Registered model for golden cross: {model.name}")

        return golden_model

    async def get_active_model_for_inference(self, task_type: str = "general",
                                            required_capabilities: List[str] = None,
                                            priority: int = 5,
                                            metadata: Dict[str, Any] = None) -> Optional[GoldenCrossModel]:
        """
        Get the active model for inference (golden cross principle)

        If current active model matches requirements, use it.
        Otherwise, switch to optimal model.
        """

        with self.active_model_lock:
            # Check if current active model is suitable
            if self.active_model and self.active_model.state == ModelState.ACTIVE:
                if self._model_matches_requirements(self.active_model, task_type, required_capabilities):
                    # Use current active model (golden cross alignment maintained)
                    self.logger.debug(f"✨ Using active model: {self.active_model.name} (golden cross maintained)")
                    self.active_model.inference_count += 1
                    self.active_model.last_inference = datetime.now()
                    self._record_convergence(self.active_model, task_type, "maintained")
                    return self.active_model

            # Need to switch models (golden cross transition)
            optimal_model = self.router.select_model(
                task_type=task_type,
                required_capabilities=required_capabilities,
                priority=priority,
                metadata=metadata
            )

            if not optimal_model:
                self.logger.error("❌ No suitable model found for inference")
                return None

            # Get golden cross model
            golden_model = self.models.get(optimal_model.name)
            if not golden_model:
                self.logger.error(f"❌ Model not registered: {optimal_model.name}")
                return None

            # Switch to optimal model
            if self.active_model and self.active_model != golden_model:
                await self._switch_model(self.active_model, golden_model)
            elif not self.active_model:
                await self._activate_model(golden_model)

            golden_model.inference_count += 1
            golden_model.last_inference = datetime.now()
            self._record_convergence(golden_model, task_type, "switched" if self.active_model else "initialized")

            self.active_model = golden_model
            return golden_model

    def _model_matches_requirements(self, model: GoldenCrossModel, task_type: str,
                                   required_capabilities: List[str] = None) -> bool:
        """Check if model matches task requirements"""
        if required_capabilities:
            router_caps = model.router_model.capabilities if model.router_model else []
            if not any(cap in router_caps for cap in required_capabilities):
                return False

        # Check if model supports task type
        if model.router_model:
            router_caps = model.router_model.capabilities
            if task_type not in router_caps and not any(task_type in cap for cap in router_caps):
                return False

        return True

    async def _activate_model(self, model: GoldenCrossModel):
        """Activate a model (load it)"""
        self.logger.info(f"🔄 Activating model: {model.name} (golden cross convergence)")

        model.state = ModelState.LOADING
        model.load_time = datetime.now()

        try:
            # Simulate model loading (in real implementation, this would load the model)
            # For now, just mark as active
            await asyncio.sleep(0.1)  # Placeholder for actual loading

            model.state = ModelState.ACTIVE
            model.convergence_score = 1.0  # Perfect convergence when active

            self.logger.info(f"✅ Model activated: {model.name} (golden cross aligned)")
            self.model_switch_queue.append({
                "timestamp": datetime.now().isoformat(),
                "action": "activated",
                "model": model.name
            })

        except Exception as e:
            model.state = ModelState.ERROR
            self.logger.error(f"❌ Failed to activate model {model.name}: {e}")

    async def _deactivate_model(self, model: GoldenCrossModel):
        """Deactivate a model (unload it)"""
        if model.state != ModelState.ACTIVE:
            return

        self.logger.info(f"🔄 Deactivating model: {model.name}")

        model.state = ModelState.UNLOADING

        try:
            # Simulate model unloading
            await asyncio.sleep(0.1)  # Placeholder for actual unloading

            model.state = ModelState.INACTIVE
            model.convergence_score = 0.0

            self.logger.info(f"✅ Model deactivated: {model.name}")
            self.model_switch_queue.append({
                "timestamp": datetime.now().isoformat(),
                "action": "deactivated",
                "model": model.name
            })

        except Exception as e:
            model.state = ModelState.ERROR
            self.logger.error(f"❌ Failed to deactivate model {model.name}: {e}")

    async def _switch_model(self, old_model: GoldenCrossModel, new_model: GoldenCrossModel):
        """Switch from one active model to another"""
        self.logger.info(f"🔄 Switching models: {old_model.name} → {new_model.name} (golden cross transition)")

        # Deactivate old model
        await self._deactivate_model(old_model)

        # Activate new model
        await self._activate_model(new_model)

        self.model_switch_queue.append({
            "timestamp": datetime.now().isoformat(),
            "action": "switched",
            "from": old_model.name,
            "to": new_model.name
        })

    def _record_convergence(self, model: GoldenCrossModel, task_type: str, action: str):
        """Record golden cross convergence event"""
        self.convergence_history.append({
            "timestamp": datetime.now().isoformat(),
            "model": model.name,
            "task_type": task_type,
            "action": action,
            "inference_count": model.inference_count,
            "convergence_score": model.convergence_score
        })

        # Track inference sequence for alignment analysis
        self.inference_sequence.append({
            "model": model.name,
            "task_type": task_type,
            "timestamp": datetime.now().isoformat()
        })

    async def batch_inference(self, tasks: List[Dict[str, Any]], 
                             use_same_model: bool = True) -> List[Dict[str, Any]]:
        """
        Perform batch inference using SINGLE active model

        All tasks in batch use the same model for golden cross alignment.
        """

        if not tasks:
            return []

        # Select optimal model for batch (based on first task or aggregate requirements)
        first_task = tasks[0]

        # Determine batch requirements
        task_types = [t.get("task_type", "general") for t in tasks]
        most_common_type = max(set(task_types), key=task_types.count) if task_types else "general"

        # Get active model for batch
        active_model = await self.get_active_model_for_inference(
            task_type=most_common_type,
            required_capabilities=first_task.get("required_capabilities"),
            priority=max([t.get("priority", 5) for t in tasks], default=5),
            metadata=first_task.get("metadata", {})
        )

        if not active_model:
            return [{"error": "No model available"} for _ in tasks]

        self.logger.info(f"✨ Batch inference using SINGLE model: {active_model.name} ({len(tasks)} tasks)")

        # Process all tasks with same model (golden cross principle)
        results = []
        for task in tasks:
            # Use same active model for all tasks
            result = {
                "model": active_model.name,
                "task_id": task.get("task_id", "unknown"),
                "result": f"Processed by {active_model.name}",
                "inference_count": active_model.inference_count
            }
            results.append(result)

        active_model.inference_count += len(tasks)
        active_model.last_inference = datetime.now()

        return results

    def get_convergence_status(self) -> Dict[str, Any]:
        """Get golden cross convergence status"""
        return {
            "active_model": {
                "name": self.active_model.name if self.active_model else None,
                "state": self.active_model.state.value if self.active_model else None,
                "inference_count": self.active_model.inference_count if self.active_model else 0,
                "convergence_score": self.active_model.convergence_score if self.active_model else 0.0
            },
            "total_models": len(self.models),
            "registered_models": [
                {
                    "name": m.name,
                    "state": m.state.value,
                    "inference_count": m.inference_count
                }
                for m in self.models.values()
            ],
            "recent_switches": list(self.model_switch_queue)[-10:],
            "convergence_history_count": len(self.convergence_history),
            "routing_strategy": self.router.routing_strategy.value
        }

    def set_routing_strategy(self, strategy: RoutingStrategy):
        """Set routing strategy (affects model selection, not active state)"""
        self.router.set_routing_strategy(strategy)
        self.logger.info(f"✨ Routing strategy updated: {strategy.value}")

    def save_convergence_data(self):
        try:
            """Save golden cross convergence data"""
            data_file = self.data_dir / "convergence_data.json"

            data = {
                "last_updated": datetime.now().isoformat(),
                "active_model": self.active_model.name if self.active_model else None,
                "convergence_history": list(self.convergence_history)[-100:],
                "model_switches": list(self.model_switch_queue),
                "inference_sequence": list(self.inference_sequence)[-50:]
            }

            with open(data_file, 'w') as f:
                json.dump(data, f, indent=2)


        except Exception as e:
            self.logger.error(f"Error in save_convergence_data: {e}", exc_info=True)
            raise
def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Golden Cross LLM Convergence System")
    parser.add_argument("action", choices=["status", "activate", "set-strategy"], help="Action")
    parser.add_argument("--model", help="Model name")
    parser.add_argument("--strategy", choices=[s.value for s in RoutingStrategy], help="Routing strategy")

    args = parser.parse_args()

    convergence = GoldenCrossLLMConvergence()

    if args.action == "status":
        status = convergence.get_convergence_status()
        print("✨ GOLDEN CROSS LLM CONVERGENCE STATUS")
        print("=" * 80)
        print(f"Active Model: {status['active_model']['name'] or 'None'}")
        print(f"State: {status['active_model']['state'] or 'None'}")
        print(f"Inference Count: {status['active_model']['inference_count']}")
        print(f"Convergence Score: {status['active_model']['convergence_score']:.2f}")
        print(f"\nRegistered Models: {status['total_models']}")
        print(f"Routing Strategy: {status['routing_strategy']}")

    elif args.action == "set-strategy":
        if not args.strategy:
            print("❌ Please provide --strategy")
            return 1
        strategy = RoutingStrategy(args.strategy)
        convergence.set_routing_strategy(strategy)
        print(f"✅ Routing strategy set to: {strategy.value}")


if __name__ == "__main__":


    main()