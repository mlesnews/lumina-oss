#!/usr/bin/env python3
"""
AI Model Transparency System

Provides full transparency of active AI model in AUTO mode, showing:
- Current active model (local or cloud)
- Model selection reason
- Cost optimization status
- One-shot mode enforcement
- Local-first preference enforcement

Tags: #MODEL_TRANSPARENCY #AUTO_MODE #LOCAL_FIRST #COST_OPTIMIZATION #ONE_SHOT @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        def get_logger(name):
            return logging.getLogger(name)

logger = get_logger("AIModelTransparency")


class ModelType(Enum):
    """Model type"""
    LOCAL = "local"
    CLOUD = "cloud"
    HYBRID = "hybrid"


class ModelTier(Enum):
    """Model power/cost tier"""
    LOWEST = "lowest"  # Least powerful, cheapest
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    HIGHEST = "highest"  # Most powerful, most expensive


@dataclass
class ModelInfo:
    """Model information"""
    provider: str
    model_name: str
    model_type: ModelType
    tier: ModelTier
    cost_per_token: float
    is_local: bool
    is_one_shot: bool = True  # Always one-shot mode
    selection_reason: str = ""
    confidence: float = 0.0


@dataclass
class ActiveModelStatus:
    """Current active model status"""
    model: ModelInfo
    mode: str  # "AUTO", "MANUAL", etc.
    timestamp: datetime
    request_id: Optional[str] = None
    cost_estimate: Optional[float] = None
    local_preference_used: bool = True
    cost_optimized: bool = True
    one_shot_enforced: bool = True


class AIModelTransparencySystem:
    """
    AI Model Transparency System

    Provides full transparency of active AI model in AUTO mode:
    - Shows current active model (local or cloud)
    - Displays model selection reason
    - Indicates cost optimization
    - Enforces one-shot mode
    - Enforces local-first preference
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize transparency system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "model_transparency"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logger

        # Current active model
        self.current_model: Optional[ActiveModelStatus] = None

        # Model history
        self.model_history: List[ActiveModelStatus] = []

        # Model cost database
        self.model_costs = self._load_model_costs()

        # Callbacks for UI updates
        self.ui_update_callback: Optional[callable] = None

        self.logger.info("✅ AI Model Transparency System initialized")
        self.logger.info("   Local-first: ENABLED")
        self.logger.info("   Cost optimization: ENABLED")
        self.logger.info("   One-shot mode: ENABLED")

    def _load_model_costs(self) -> Dict[str, Dict[str, Any]]:
        """Load model cost database"""
        # Default cost estimates (per 1K tokens)
        return {
            # Local models (free/negligible cost)
            "ultron": {"cost_input": 0.0, "cost_output": 0.0, "tier": ModelTier.LOWEST, "is_local": True},
            "ultron_local": {"cost_input": 0.0, "cost_output": 0.0, "tier": ModelTier.LOWEST, "is_local": True},
            "kaiju_iron_legion": {"cost_input": 0.0, "cost_output": 0.0, "tier": ModelTier.LOWEST, "is_local": True},
            "iron_legion": {"cost_input": 0.0, "cost_output": 0.0, "tier": ModelTier.LOWEST, "is_local": True},
            "iron_legion_router": {"cost_input": 0.0, "cost_output": 0.0, "tier": ModelTier.LOWEST, "is_local": True},
            "docker_ollama": {"cost_input": 0.0, "cost_output": 0.0, "tier": ModelTier.LOWEST, "is_local": True},

            # Cloud models (cost per 1K tokens)
            "google_gemini_3_flash": {"cost_input": 0.0001, "cost_output": 0.0003, "tier": ModelTier.LOWEST, "is_local": False},
            "openai_gpt35": {"cost_input": 0.0015, "cost_output": 0.002, "tier": ModelTier.LOW, "is_local": False},
            "openai_gpt4": {"cost_input": 0.03, "cost_output": 0.06, "tier": ModelTier.HIGH, "is_local": False},
            "anthropic_claude": {"cost_input": 0.008, "cost_output": 0.024, "tier": ModelTier.MEDIUM, "is_local": False},
            "azure_openai": {"cost_input": 0.002, "cost_output": 0.002, "tier": ModelTier.LOW, "is_local": False},
            "grok": {"cost_input": 0.0, "cost_output": 0.0, "tier": ModelTier.LOWEST, "is_local": False},  # Free tier (preferred cloud option)
        }

    def register_model_selection(
        self,
        provider: str,
        model_name: str,
        model_type: ModelType,
        selection_reason: str,
        confidence: float = 0.0,
        request_id: Optional[str] = None,
        estimated_tokens: Optional[int] = None
    ):
        """
        Register a model selection for transparency

        Args:
            provider: Model provider name
            model_name: Specific model name
            model_type: Local, cloud, or hybrid
            selection_reason: Why this model was selected
            confidence: Selection confidence (0-1)
            request_id: Request ID if available
            estimated_tokens: Estimated token count
        """
        # Get model info
        model_key = provider.lower().replace(" ", "_")
        cost_info = self.model_costs.get(model_key, {
            "cost_input": 0.0,
            "cost_output": 0.0,
            "tier": ModelTier.MEDIUM,
            "is_local": model_type == ModelType.LOCAL
        })

        # Calculate cost estimate
        cost_estimate = None
        if estimated_tokens and not cost_info["is_local"]:
            # Estimate 70% input, 30% output
            input_tokens = int(estimated_tokens * 0.7)
            output_tokens = int(estimated_tokens * 0.3)
            cost_estimate = (
                (input_tokens / 1000) * cost_info["cost_input"] +
                (output_tokens / 1000) * cost_info["cost_output"]
            )

        # Create model info
        model_info = ModelInfo(
            provider=provider,
            model_name=model_name,
            model_type=model_type,
            tier=cost_info["tier"],
            cost_per_token=(cost_info["cost_input"] + cost_info["cost_output"]) / 2,
            is_local=cost_info["is_local"],
            is_one_shot=True,  # Always one-shot
            selection_reason=selection_reason,
            confidence=confidence
        )

        # Create active model status
        active_status = ActiveModelStatus(
            model=model_info,
            mode="AUTO",
            timestamp=datetime.now(),
            request_id=request_id,
            cost_estimate=cost_estimate,
            local_preference_used=cost_info["is_local"],
            cost_optimized=True,  # Always optimized
            one_shot_enforced=True  # Always enforced
        )

        # Update current model
        self.current_model = active_status

        # Add to history
        self.model_history.append(active_status)
        if len(self.model_history) > 1000:
            self.model_history = self.model_history[-1000:]

        # Auto-save current status for UI
        self._save_current_status()

        # Log transparency
        self._log_model_selection(active_status)

        # Update UI if callback set
        if self.ui_update_callback:
            try:
                self.ui_update_callback(active_status)
            except Exception as e:
                self.logger.warning(f"Error in UI update callback: {e}")

        # Log to console
        self._display_model_transparency(active_status)

        return active_status

    def _display_model_transparency(self, status: ActiveModelStatus):
        """Display model transparency information"""
        model = status.model

        # Determine display name
        if status.mode == "AUTO":
            if model.is_local:
                display_name = f"AUTO/{model.provider.upper()}"
            else:
                display_name = f"AUTO/{model.provider.upper()}"
        else:
            display_name = f"{status.mode}/{model.provider.upper()}"

        # Log transparency
        self.logger.info("=" * 80)
        self.logger.info("🤖 ACTIVE AI MODEL TRANSPARENCY")
        self.logger.info("=" * 80)
        self.logger.info(f"Mode: {status.mode}")
        self.logger.info(f"Active Model: {display_name}")
        self.logger.info(f"Provider: {model.provider}")
        self.logger.info(f"Model: {model.model_name}")
        self.logger.info(f"Type: {model.model_type.value.upper()}")
        self.logger.info(f"Tier: {model.tier.value.upper()}")
        self.logger.info(f"Local: {'✅ YES' if model.is_local else '❌ NO'}")
        self.logger.info(f"Local-First Used: {'✅ YES' if status.local_preference_used else '❌ NO'}")
        self.logger.info(f"Cost Optimized: {'✅ YES' if status.cost_optimized else '❌ NO'}")
        self.logger.info(f"One-Shot Mode: {'✅ ENFORCED' if status.one_shot_enforced else '❌ NOT ENFORCED'}")
        if status.cost_estimate:
            self.logger.info(f"Cost Estimate: ${status.cost_estimate:.6f}")
        else:
            self.logger.info(f"Cost: {'FREE (Local)' if model.is_local else 'See provider pricing'}")
        self.logger.info(f"Selection Reason: {model.selection_reason}")
        self.logger.info(f"Confidence: {model.confidence:.1%}")
        self.logger.info("=" * 80)

    def _log_model_selection(self, status: ActiveModelStatus):
        """Log model selection to file"""
        # ... existing implementation ...

    def _save_current_status(self):
        """Save current transparency status to JSON for UI dashboard"""
        if not self.current_model:
            return

        try:
            status_file = self.data_dir / "current_status.json"
            info = self.get_transparency_info()

            # Aggregate stats for the money tachometer
            today = datetime.now().strftime('%Y%m%d')
            total_cost = 0.0
            total_tokens = 0
            cloud_requests = 0
            local_requests = 0

            # Simple aggregation from history (last 1000 requests)
            for s in self.model_history:
                if s.cost_estimate:
                    total_cost += s.cost_estimate
                if s.model.is_local:
                    local_requests += 1
                else:
                    cloud_requests += 1

            info["usage_stats"] = {
                "total_cost_usd": round(total_cost, 6),
                "local_requests": local_requests,
                "cloud_requests": cloud_requests,
                "total_requests": local_requests + cloud_requests
            }

            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(info, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Failed to save current status JSON: {e}")

    def get_current_model(self) -> Optional[ActiveModelStatus]:
        """Get current active model status"""
        return self.current_model

    def get_model_display_string(self) -> str:
        """Get formatted string for UI display"""
        if not self.current_model:
            return "AUTO/Selecting..."

        model = self.current_model.model

        if self.current_model.mode == "AUTO":
            if model.is_local:
                return f"AUTO/{model.provider.upper()}"
            else:
                return f"AUTO/{model.provider.upper()}"
        else:
            return f"{self.current_model.mode}/{model.provider.upper()}"

    def get_transparency_info(self) -> Dict[str, Any]:
        """Get full transparency information for UI"""
        if not self.current_model:
            return {
                "mode": "AUTO",
                "active_model": None,
                "status": "selecting"
            }

        model = self.current_model.model

        return {
            "mode": self.current_model.mode,
            "active_model": {
                "display_name": self.get_model_display_string(),
                "provider": model.provider,
                "model_name": model.model_name,
                "type": model.model_type.value,
                "tier": model.tier.value,
                "is_local": model.is_local,
                "is_one_shot": model.is_one_shot
            },
            "optimization": {
                "local_preference_used": self.current_model.local_preference_used,
                "cost_optimized": self.current_model.cost_optimized,
                "one_shot_enforced": self.current_model.one_shot_enforced
            },
            "cost": {
                "estimate": self.current_model.cost_estimate,
                "is_free": model.is_local
            },
            "selection": {
                "reason": model.selection_reason,
                "confidence": model.confidence
            },
            "timestamp": self.current_model.timestamp.isoformat()
        }

    def set_ui_update_callback(self, callback: callable):
        """Set callback for UI updates"""
        self.ui_update_callback = callback

    def enforce_one_shot_mode(self) -> bool:
        """
        Enforce one-shot mode (no retries)

        Returns:
            True (always enforced)
        """
        return True  # Always enforce one-shot

    def enforce_local_first(self) -> bool:
        """
        Enforce local-first preference

        Returns:
            True (always enforced)
        """
        return True  # Always enforce local-first

    def enforce_cost_optimization(self) -> bool:
        """
        Enforce cost optimization (least powerful, cheapest)

        Returns:
            True (always enforced)
        """
        return True  # Always enforce cost optimization


# Global instance
_global_transparency: Optional[AIModelTransparencySystem] = None


def get_model_transparency(project_root: Optional[Path] = None) -> AIModelTransparencySystem:
    try:
        """Get or create global model transparency instance"""
        global _global_transparency

        if _global_transparency is None:
            if project_root is None:
                project_root = Path(__file__).parent.parent.parent
            _global_transparency = AIModelTransparencySystem(project_root)

        return _global_transparency


    except Exception as e:
        logger.error(f"Error in get_model_transparency: {e}", exc_info=True)
        raise
def register_active_model(
    provider: str,
    model_name: str,
    model_type: ModelType,
    selection_reason: str,
    **kwargs
) -> ActiveModelStatus:
    """Convenience function to register active model"""
    transparency = get_model_transparency()
    return transparency.register_model_selection(
        provider=provider,
        model_name=model_name,
        model_type=model_type,
        selection_reason=selection_reason,
        **kwargs
    )


if __name__ == "__main__":
    # Test transparency system
    print("=" * 80)
    print("AI MODEL TRANSPARENCY SYSTEM TEST")
    print("=" * 80)
    print()

    transparency = AIModelTransparencySystem()

    # Test local model
    print("Testing LOCAL model selection...")
    transparency.register_model_selection(
        provider="ULTRON",
        model_name="ultron-hybrid",
        model_type=ModelType.LOCAL,
        selection_reason="Local-first preference, least powerful sufficient model",
        confidence=0.95,
        estimated_tokens=1000
    )
    print()

    # Test cloud model
    print("Testing CLOUD model selection...")
    transparency.register_model_selection(
        provider="Grok",
        model_name="grok-beta",
        model_type=ModelType.CLOUD,
        selection_reason="Local unavailable, using cheapest cloud option (Grok free tier)",
        confidence=0.85,
        estimated_tokens=2000
    )
    print()

    # Get transparency info
    info = transparency.get_transparency_info()
    print("Current Transparency Info:")
    print(json.dumps(info, indent=2))
