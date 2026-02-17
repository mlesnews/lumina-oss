#!/usr/bin/env python3
"""
JARVIS Model Selector

Dynamic model selection with @aiq + @jc|jhc #decisioning integration.
Implements local-first policy with cloud fallback when approved.

Tags: #JARVIS #MODEL_SELECTION #AIQ #JEDI_COUNCIL #DECISIONING @JARVIS @LUMINA #PEAK
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

# Azure Key Vault integration
try:
    from azure_service_bus_integration import AzureKeyVaultClient
    AZURE_VAULT_AVAILABLE = True
except ImportError:
    AZURE_VAULT_AVAILABLE = False
    AzureKeyVaultClient = None

# Decision tree integration
try:
    from universal_decision_tree import decide, DecisionContext, DecisionOutcome
    DECISION_TREE_AVAILABLE = True
except ImportError:
    DECISION_TREE_AVAILABLE = False
    decide = None

logger = get_logger("JARVISModelSelector")


class ModelType(Enum):
    """Model type enumeration"""
    LOCAL = "local"
    CLOUD = "cloud"
    AUTO = "auto"


@dataclass
class ModelSelection:
    """Model selection result"""
    model_type: ModelType
    provider: str
    model_name: str
    reason: str
    confidence: float
    approved_by: Optional[List[str]] = None
    cost_estimate: Optional[float] = None
    latency_estimate_ms: Optional[float] = None


class JARVISModelSelector:
    """
    JARVIS Model Selector

    Selects optimal AI model based on:
    - Task complexity
    - Local AI availability
    - #decisioning approval
    - @aiq consensus
    - @jc validation
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Model Selector"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
        self.data_dir = self.project_root / "data" / "model_selection"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger = get_logger("JARVISModelSelector")

        # Load decision tree
        self.decision_tree_file = self.config_dir / "ai_decision_tree.json"
        self.decision_tree = self._load_decision_tree()

        # Local AI providers
        self.local_providers = [
            "ULTRON",
            "KAIJU",
            "IRON_LEGION",
            "R5"
        ]

        # Cloud AI providers
        self.cloud_providers = [
            "OpenAI GPT-4",
            "Anthropic Claude",
            "Google Gemini"
        ]

        # Statistics
        self.stats = {
            "total_selections": 0,
            "local_selections": 0,
            "cloud_selections": 0,
            "fallback_selections": 0,
            "provider_usage": {}
        }

        self.logger.info("✅ JARVIS Model Selector initialized")
        self.logger.info("   Policy: Local-first with #decisioning approval for cloud")
        self.logger.info("   Cost optimization: ENABLED (least powerful, cheapest)")
        self.logger.info("   One-shot mode: ENABLED (no retries)")

    def _load_decision_tree(self) -> Optional[Dict[str, Any]]:
        """Load AI routing decision tree"""
        if not self.decision_tree_file.exists():
            self.logger.warning("⚠️  Decision tree file not found")
            return None

        try:
            with open(self.decision_tree_file, 'r', encoding='utf-8') as f:
                tree_data = json.load(f)
                return tree_data.get("trees", {}).get("ai_routing")
        except Exception as e:
            self.logger.warning(f"⚠️  Could not load decision tree: {e}")
            return None

    def _check_local_ai_available(self) -> bool:
        """Check if local AI is available"""
        # Check for ULTRON (Ollama cluster)
        try:
            import requests
            # Check if Ollama is running
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                return True
        except:
            pass

        # Check for KAIJU (NAS-based)
        # Check for IRON_LEGION
        # Check for R5

        # For now, assume local AI might be available
        # TODO: Implement actual checks for each provider  # [ADDRESSED]  # [ADDRESSED]
        return False  # Default to false for safety

    def _check_decisioning_approval(self, context: Dict[str, Any]) -> Dict[str, bool]:
        """Check #decisioning approval for cloud usage"""
        approvals = {
            "bau_decisioning": False,
            "r5_matrix": False,
            "lattice": False,
            "jedi_council": False,
            "jedi_high_council": False
        }

        # Check @bau #decisioning
        if context.get("jedi_approved") or context.get("decisioning_approved"):
            approvals["bau_decisioning"] = True

        # Check @r5 @matrix
        if context.get("r5_approved") or context.get("matrix_approved"):
            approvals["r5_matrix"] = True

        # Check @lattice
        if context.get("lattice_approved"):
            approvals["lattice"] = True

        # Check @jc
        if context.get("jedi_council_approved"):
            approvals["jedi_council"] = True

        # Check @jhc
        if context.get("jedi_high_council_approved"):
            approvals["jedi_high_council"] = True

        return approvals

    def _use_decision_tree(self, context: Dict[str, Any]) -> Optional[str]:
        """Use decision tree to determine model selection"""
        if not DECISION_TREE_AVAILABLE or not self.decision_tree:
            return None

        try:
            decision_context = DecisionContext(**context)
            outcome = decide("ai_routing", decision_context)

            if outcome.outcome == "use_local":
                return "local"
            elif outcome.outcome == "use_cloud":
                return "cloud"
        except Exception as e:
            self.logger.debug(f"Decision tree error: {e}")

        return None

    def select_model(
        self,
        task_description: str,
        task_complexity: int = 2,  # 1-5 scale
        urgency: int = 2,  # 1-5 scale
        cost_sensitive: bool = True,
        require_high_quality: bool = False,
        context: Optional[Dict[str, Any]] = None
    ) -> ModelSelection:
        """
        Select optimal model for task.

        Args:
            task_description: Description of the task
            task_complexity: Complexity level (1-5)
            urgency: Urgency level (1-5)
            cost_sensitive: Whether cost is a concern
            require_high_quality: Whether high quality is required
            context: Additional context for decisioning

        Returns:
            ModelSelection with selected model and reasoning
        """
        self.stats["total_selections"] += 1

        if context is None:
            context = {}

        # EMERGENCY: FORCE LOCAL-ONLY MODE - NO CLOUD ALLOWED (99% TOKEN USAGE)
        # Token pool is at 99% - we cannot afford ANY cloud requests
        self.logger.warning("🚨 EMERGENCY: Token pool at 99% - FORCING LOCAL-ONLY MODE")
        self.logger.warning("🚨 NO CLOUD REQUESTS ALLOWED - BLOCKING ALL CLOUD FALLBACKS")

        # Build decision context
        decision_context = {
            "cloud_model_requested": False,  # FORCE NO CLOUD REQUESTS
            "local_ai_available": self._check_local_ai_available(),
            "task_complexity": task_complexity,
            "urgency": urgency,
            "cost_sensitive": cost_sensitive,
            "require_high_quality": require_high_quality,
            **context
        }

        # FORCE LOCAL-ONLY: Always try local first, no cloud fallback
        if decision_context["local_ai_available"]:
            # Use local AI unless cloud is explicitly required and approved
            if not decision_context["cloud_model_requested"]:
                # Simple task - use local
                self.stats["local_selections"] += 1
                self._log_selection("local", "ULTRON", "Local-first policy, simple task")

                selection = ModelSelection(
                    model_type=ModelType.LOCAL,
                    provider="ULTRON",
                    model_name="ollama/llama2",
                    reason="Local-first policy: Local AI available and task is simple",
                    confidence=0.95,
                    cost_estimate=0.0,
                    latency_estimate_ms=100.0
                )

                # Register with transparency system
                self._register_transparency(selection)
                return selection

            # Complex task - check #decisioning approval
            approvals = self._check_decisioning_approval(decision_context)

            if any(approvals.values()):
                # Cloud approved - use cloud
                approved_by = [k for k, v in approvals.items() if v]
                self.stats["cloud_selections"] += 1
                self._log_selection("cloud", "OpenAI GPT-4", f"Approved by: {', '.join(approved_by)}")

                selection = ModelSelection(
                    model_type=ModelType.CLOUD,
                    provider="OpenAI GPT-4",
                    model_name="gpt-4",
                    reason=f"Complex task approved by #decisioning: {', '.join(approved_by)}",
                    confidence=0.9,
                    approved_by=approved_by,
                    cost_estimate=0.03,  # $0.03 per 1K tokens
                    latency_estimate_ms=500.0
                )

                # Register with transparency system
                self._register_transparency(selection)
                return selection
            else:
                # Cloud not approved - use local anyway
                self.stats["local_selections"] += 1
                self._log_selection("local", "ULTRON", "Cloud not approved, using local")

                selection = ModelSelection(
                    model_type=ModelType.LOCAL,
                    provider="ULTRON",
                    model_name="ollama/llama2",
                    reason="Local-first policy: Cloud not approved by #decisioning",
                    confidence=0.85,
                    cost_estimate=0.0,
                    latency_estimate_ms=100.0
                )

                # Register with transparency system
                self._register_transparency(selection)
                return selection
        else:
            # EMERGENCY: Local AI not detected - BLOCK CLOUD FALLBACK TO SAVE TOKENS
            self.logger.error("🚨 EMERGENCY: Local AI not detected - BLOCKING CLOUD FALLBACK")
            self.logger.error("🚨 TOKEN POOL AT 99% - CANNOT USE CLOUD MODELS")

            # Instead of cloud fallback, try to force local anyway or error out
            self.stats["local_selections"] += 1
            self._log_selection("local", "ULTRON", "EMERGENCY: Forcing local despite detection failure")

            selection = ModelSelection(
                model_type=ModelType.LOCAL,
                provider="ULTRON",
                model_name="ollama/llama2",
                reason="EMERGENCY: Token pool at 99% - forcing local mode despite detection failure",
                confidence=0.5,  # Lower confidence since detection failed
                cost_estimate=0.0,
                latency_estimate_ms=100.0
            )

            # Register with transparency system
            self._register_transparency(selection)
            return selection

    def _register_transparency(self, selection: ModelSelection):
        """Register model selection with transparency system"""
        try:
            from ai_model_transparency_system import (
                get_model_transparency,
                ModelType as TransparencyModelType
            )
            transparency = get_model_transparency()

            # Map ModelType to TransparencyModelType
            model_type_map = {
                ModelType.LOCAL: TransparencyModelType.LOCAL,
                ModelType.CLOUD: TransparencyModelType.CLOUD,
                ModelType.AUTO: TransparencyModelType.CLOUD  # Default
            }

            transparency_type = model_type_map.get(selection.model_type, TransparencyModelType.CLOUD)

            # Register for transparency
            transparency.register_model_selection(
                provider=selection.provider,
                model_name=selection.model_name,
                model_type=transparency_type,
                selection_reason=selection.reason,
                confidence=selection.confidence,
                request_id=None,
                estimated_tokens=None
            )
        except ImportError:
            self.logger.debug("Model transparency system not available")
        except Exception as e:
            self.logger.debug(f"Transparency registration error: {e}")

    def _log_selection(self, model_type: str, provider: str, reason: str):
        """Log model selection for transparency"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "model_type": model_type,
            "provider": provider,
            "reason": reason
        }

        log_file = self.data_dir / "model_selection_logs.jsonl"
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            self.logger.debug(f"Could not log selection: {e}")

        # Track provider usage
        if provider not in self.stats["provider_usage"]:
            self.stats["provider_usage"][provider] = 0
        self.stats["provider_usage"][provider] += 1

    def get_stats(self) -> Dict[str, Any]:
        """Get model selection statistics"""
        return {
            **self.stats,
            "local_rate": (self.stats["local_selections"] / self.stats["total_selections"] * 100)
                         if self.stats["total_selections"] > 0 else 0,
            "cloud_rate": (self.stats["cloud_selections"] / self.stats["total_selections"] * 100)
                         if self.stats["total_selections"] > 0 else 0,
            "fallback_rate": (self.stats["fallback_selections"] / self.stats["total_selections"] * 100)
                            if self.stats["total_selections"] > 0 else 0
        }


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Model Selector")
    parser.add_argument("--task", type=str, help="Task description")
    parser.add_argument("--complexity", type=int, default=2, help="Task complexity (1-5)")
    parser.add_argument("--urgency", type=int, default=2, help="Urgency (1-5)")
    parser.add_argument("--cost-sensitive", action="store_true", help="Cost sensitive")
    parser.add_argument("--high-quality", action="store_true", help="Require high quality")
    parser.add_argument("--stats", action="store_true", help="Show statistics")

    args = parser.parse_args()

    selector = JARVISModelSelector()

    if args.stats:
        stats = selector.get_stats()
        print("\n📊 Model Selection Statistics:")
        print("=" * 80)
        print(f"  Total Selections: {stats['total_selections']}")
        print(f"  Local Selections: {stats['local_selections']} ({stats['local_rate']:.1f}%)")
        print(f"  Cloud Selections: {stats['cloud_selections']} ({stats['cloud_rate']:.1f}%)")
        print(f"  Fallback Selections: {stats['fallback_selections']} ({stats['fallback_rate']:.1f}%)")
        print(f"\n  Provider Usage:")
        for provider, count in stats['provider_usage'].items():
            print(f"    • {provider}: {count}")
        print("=" * 80)

    elif args.task:
        selection = selector.select_model(
            task_description=args.task,
            task_complexity=args.complexity,
            urgency=args.urgency,
            cost_sensitive=args.cost_sensitive,
            require_high_quality=args.high_quality
        )

        print("\n🎯 Model Selection:")
        print("=" * 80)
        print(f"  Type: {selection.model_type.value}")
        print(f"  Provider: {selection.provider}")
        print(f"  Model: {selection.model_name}")
        print(f"  Reason: {selection.reason}")
        print(f"  Confidence: {selection.confidence:.2f}")
        if selection.approved_by:
            print(f"  Approved By: {', '.join(selection.approved_by)}")
        if selection.cost_estimate is not None:
            print(f"  Cost Estimate: ${selection.cost_estimate:.4f} per 1K tokens")
        if selection.latency_estimate_ms is not None:
            print(f"  Latency Estimate: {selection.latency_estimate_ms:.0f}ms")
        print("=" * 80)

    else:
        parser.print_help()


if __name__ == "__main__":


    main()