#!/usr/bin/env python3
"""
⚡ ULTRON WARP FACTOR CONTROLLER
                    -LUM THE MODERN

Dynamic scaling system to dial compute intensity from "LUDICROUS SPEED!" 
down to sustainable "Warp Factor 9" based on budget and needs.

WARP FACTOR SCALE:
┌─────────────────────────────────────────────────────────────────────────────┐
│  Warp 1-3:   Local only (FREE)                    │  $0/month             │
│  Warp 4-6:   Local + Subscriptions (FLAT)          │  ~$30/month           │
│  Warp 7-8:   Local + Occasional Cloud              │  ~$50-100/month       │
│  Warp 9:     Smart Hybrid (90% local, 10% cloud)  │  ~$100-200/month      │
│  Warp 10:    Heavy Cloud Usage                     │  ~$500-1000/month     │
│  LUDICROUS:  ALL THE THINGS ALL THE TIME           │  ~$5000+/month        │
└─────────────────────────────────────────────────────────────────────────────┘

@LUMINA @JARVIS @ULTRON -LUM_THE_MODERN
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import IntEnum
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("ULTRONWarpFactor")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ULTRONWarpFactor")


class WarpFactor(IntEnum):
    """Warp Factor levels - from sustainable to ludicrous"""
    WARP_1 = 1   # Local only, smallest models
    WARP_2 = 2   # Local only, medium models
    WARP_3 = 3   # Local only, all models
    WARP_4 = 4   # Local + Subscriptions (Cursor Pro, Copilot)
    WARP_5 = 5   # Local + Subscriptions + Light cloud
    WARP_6 = 6   # Local + Subscriptions + Moderate cloud
    WARP_7 = 7   # Local + Occasional cloud (complex tasks)
    WARP_8 = 8   # Local + Regular cloud (quality tasks)
    WARP_9 = 9   # Smart Hybrid (90% local, 10% cloud) - RECOMMENDED
    WARP_10 = 10 # Heavy cloud usage
    LUDICROUS = 11  # ALL THE THINGS - Not sustainable


@dataclass
class WarpFactorConfig:
    """Configuration for a warp factor level"""
    level: WarpFactor
    name: str
    description: str
    local_percent: float  # 0.0 - 1.0
    subscription_percent: float
    cloud_percent: float
    estimated_monthly_cost: float
    use_parallel: bool
    max_cloud_requests_per_day: Optional[int]
    preferred_local_models: list = field(default_factory=list)
    preferred_cloud_models: list = field(default_factory=list)
    sustainability: str = "sustainable"  # sustainable, moderate, high, ludicrous


class ULTRONWarpFactorController:
    """
    Controls compute intensity based on warp factor setting.

    Default: WARP_9 (Smart Hybrid - sustainable but powerful)
    """

    def __init__(self, warp_factor: WarpFactor = WarpFactor.WARP_9):
        self.current_warp = warp_factor
        self.config_path = project_root / "config" / "ultron_warp_factor.json"
        self.configs = self._init_warp_configs()
        self._load_config()

        logger.info("=" * 80)
        logger.info("⚡ ULTRON WARP FACTOR CONTROLLER INITIALIZED")
        logger.info("=" * 80)
        logger.info(f"   Current Warp Factor: {self.current_warp.name} ({self.current_warp.value})")
        logger.info(f"   Mode: {self.configs[self.current_warp].name}")
        logger.info(f"   Est. Monthly Cost: ${self.configs[self.current_warp].estimated_monthly_cost:.2f}")
        logger.info(f"   Sustainability: {self.configs[self.current_warp].sustainability}")
        logger.info("=" * 80)

    def _init_warp_configs(self) -> Dict[WarpFactor, WarpFactorConfig]:
        """Initialize all warp factor configurations"""
        return {
            WarpFactor.WARP_1: WarpFactorConfig(
                level=WarpFactor.WARP_1,
                name="Minimal Local",
                description="Local only, smallest models (SmolLM)",
                local_percent=1.0,
                subscription_percent=0.0,
                cloud_percent=0.0,
                estimated_monthly_cost=0.0,
                use_parallel=False,
                max_cloud_requests_per_day=0,
                preferred_local_models=["smollm:135m"],
                sustainability="sustainable"
            ),
            WarpFactor.WARP_2: WarpFactorConfig(
                level=WarpFactor.WARP_2,
                name="Light Local",
                description="Local only, small-medium models",
                local_percent=1.0,
                subscription_percent=0.0,
                cloud_percent=0.0,
                estimated_monthly_cost=0.0,
                use_parallel=False,
                max_cloud_requests_per_day=0,
                preferred_local_models=["smollm:135m", "llama3.2:3b"],
                sustainability="sustainable"
            ),
            WarpFactor.WARP_3: WarpFactorConfig(
                level=WarpFactor.WARP_3,
                name="Full Local",
                description="Local only, all models available",
                local_percent=1.0,
                subscription_percent=0.0,
                cloud_percent=0.0,
                estimated_monthly_cost=0.0,
                use_parallel=True,  # Can use all 9 cores
                max_cloud_requests_per_day=0,
                preferred_local_models=["codellama:13b", "mistral:latest", "llama3:8b"],
                sustainability="sustainable"
            ),
            WarpFactor.WARP_4: WarpFactorConfig(
                level=WarpFactor.WARP_4,
                name="Local + Subscriptions",
                description="Local + Flat-rate subscriptions (Cursor Pro, Copilot)",
                local_percent=0.8,
                subscription_percent=0.2,
                cloud_percent=0.0,
                estimated_monthly_cost=30.0,
                use_parallel=True,
                max_cloud_requests_per_day=0,
                preferred_local_models=["codellama:13b", "mistral:latest"],
                sustainability="sustainable"
            ),
            WarpFactor.WARP_5: WarpFactorConfig(
                level=WarpFactor.WARP_5,
                name="Light Hybrid",
                description="Local + Subscriptions + Occasional cloud",
                local_percent=0.85,
                subscription_percent=0.1,
                cloud_percent=0.05,
                estimated_monthly_cost=50.0,
                use_parallel=True,
                max_cloud_requests_per_day=10,
                preferred_local_models=["codellama:13b", "mistral:latest"],
                preferred_cloud_models=["claude-sonnet-4"],
                sustainability="sustainable"
            ),
            WarpFactor.WARP_6: WarpFactorConfig(
                level=WarpFactor.WARP_6,
                name="Moderate Hybrid",
                description="Local + Subscriptions + Light cloud",
                local_percent=0.8,
                subscription_percent=0.1,
                cloud_percent=0.1,
                estimated_monthly_cost=100.0,
                use_parallel=True,
                max_cloud_requests_per_day=25,
                preferred_local_models=["codellama:13b", "mistral:latest"],
                preferred_cloud_models=["claude-sonnet-4", "gpt-4o"],
                sustainability="moderate"
            ),
            WarpFactor.WARP_7: WarpFactorConfig(
                level=WarpFactor.WARP_7,
                name="Balanced Hybrid",
                description="Local + Occasional cloud for complex tasks",
                local_percent=0.85,
                subscription_percent=0.05,
                cloud_percent=0.1,
                estimated_monthly_cost=150.0,
                use_parallel=True,
                max_cloud_requests_per_day=50,
                preferred_local_models=["codellama:13b", "mistral:latest"],
                preferred_cloud_models=["claude-sonnet-4"],
                sustainability="moderate"
            ),
            WarpFactor.WARP_8: WarpFactorConfig(
                level=WarpFactor.WARP_8,
                name="Quality Hybrid",
                description="Local + Regular cloud for quality tasks",
                local_percent=0.75,
                subscription_percent=0.1,
                cloud_percent=0.15,
                estimated_monthly_cost=200.0,
                use_parallel=True,
                max_cloud_requests_per_day=100,
                preferred_local_models=["codellama:13b", "mistral:latest"],
                preferred_cloud_models=["claude-opus-4", "gpt-4o"],
                sustainability="moderate"
            ),
            WarpFactor.WARP_9: WarpFactorConfig(
                level=WarpFactor.WARP_9,
                name="Smart Hybrid (RECOMMENDED)",
                description="90% local, 10% cloud - Optimal balance",
                local_percent=0.9,
                subscription_percent=0.05,
                cloud_percent=0.05,
                estimated_monthly_cost=100.0,
                use_parallel=True,
                max_cloud_requests_per_day=20,
                preferred_local_models=["codellama:13b", "mistral:latest", "llama3:8b"],
                preferred_cloud_models=["claude-opus-4"],
                sustainability="sustainable"
            ),
            WarpFactor.WARP_10: WarpFactorConfig(
                level=WarpFactor.WARP_10,
                name="Heavy Cloud",
                description="Local + Heavy cloud usage",
                local_percent=0.6,
                subscription_percent=0.1,
                cloud_percent=0.3,
                estimated_monthly_cost=1000.0,
                use_parallel=True,
                max_cloud_requests_per_day=500,
                preferred_local_models=["codellama:13b"],
                preferred_cloud_models=["claude-opus-4", "gpt-4-turbo"],
                sustainability="high"
            ),
            WarpFactor.LUDICROUS: WarpFactorConfig(
                level=WarpFactor.LUDICROUS,
                name="LUDICROUS SPEED!",
                description="ALL THE THINGS ALL THE TIME - Not sustainable",
                local_percent=0.3,
                subscription_percent=0.2,
                cloud_percent=0.5,
                estimated_monthly_cost=5000.0,
                use_parallel=True,
                max_cloud_requests_per_day=None,  # Unlimited
                preferred_local_models=["codellama:13b", "mistral:latest"],
                preferred_cloud_models=["claude-opus-4", "gpt-4-turbo", "grok-2"],
                sustainability="ludicrous"
            )
        }

    def _load_config(self):
        """Load saved warp factor from config file"""
        if self.config_path.exists():
            try:
                data = json.loads(self.config_path.read_text())
                saved_warp = WarpFactor(data.get("warp_factor", 9))
                if saved_warp in self.configs:
                    self.current_warp = saved_warp
                    logger.info(f"Loaded saved warp factor: {saved_warp.name}")
            except Exception as e:
                logger.warning(f"Could not load warp config: {e}")

    def set_warp_factor(self, warp: WarpFactor):
        try:
            """Set warp factor and save to config"""
            if warp not in self.configs:
                raise ValueError(f"Invalid warp factor: {warp}")

            self.current_warp = warp
            config = self.configs[warp]

            # Save to config file
            config_data = {
                "warp_factor": warp.value,
                "name": config.name,
                "set_at": datetime.now().isoformat(),
                "estimated_monthly_cost": config.estimated_monthly_cost,
                "sustainability": config.sustainability
            }
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            self.config_path.write_text(json.dumps(config_data, indent=2))

            logger.info(f"⚡ Warp Factor set to: {warp.name} ({warp.value})")
            logger.info(f"   Mode: {config.name}")
            logger.info(f"   Est. Cost: ${config.estimated_monthly_cost:.2f}/month")
            logger.info(f"   Sustainability: {config.sustainability}")

        except Exception as e:
            self.logger.error(f"Error in set_warp_factor: {e}", exc_info=True)
            raise
    def get_routing_decision(
        self,
        prompt: str,
        context_tokens: int = 0,
        require_frontier: bool = False
    ) -> Dict[str, Any]:
        """
        Get routing decision based on current warp factor.

        Returns decision on where to route the request.
        """
        config = self.configs[self.current_warp]

        # Check if we should use cloud
        use_cloud = False
        use_subscription = False

        # Warp 1-3: Local only
        if self.current_warp <= WarpFactor.WARP_3:
            target = "local"
            model = config.preferred_local_models[0] if config.preferred_local_models else "mistral:latest"

        # Warp 4-6: Local + Subscriptions
        elif self.current_warp <= WarpFactor.WARP_6:
            # Simple tasks → Local
            if len(prompt) < 200 and not require_frontier:
                target = "local"
                model = config.preferred_local_models[0]
            # Complex tasks → Subscription
            else:
                target = "subscription"
                model = "cursor_pro"
                use_subscription = True

        # Warp 7-9: Smart Hybrid
        elif self.current_warp <= WarpFactor.WARP_9:
            # Most tasks → Local
            if not require_frontier and context_tokens < 32000:
                target = "local"
                model = config.preferred_local_models[0]
            # Complex/frontier → Cloud
            else:
                target = "cloud"
                model = config.preferred_cloud_models[0] if config.preferred_cloud_models else "claude-opus-4"
                use_cloud = True

        # Warp 10+: Heavy cloud
        else:
            if require_frontier or context_tokens > 32000:
                target = "cloud"
                model = config.preferred_cloud_models[0]
                use_cloud = True
            else:
                target = "local"
                model = config.preferred_local_models[0]

        return {
            "warp_factor": self.current_warp.value,
            "warp_name": self.current_warp.name,
            "target": target,
            "model": model,
            "use_cloud": use_cloud,
            "use_subscription": use_subscription,
            "estimated_cost": config.estimated_monthly_cost / 30 / 100,  # Rough per-request estimate
            "reasoning": f"Warp {self.current_warp.value} ({config.name}): {config.description}"
        }

    def print_warp_status(self):
        """Print current warp factor status"""
        config = self.configs[self.current_warp]

        print("\n" + "=" * 80)
        print("⚡ ULTRON WARP FACTOR STATUS")
        print("                    -LUM THE MODERN")
        print("=" * 80)
        print(f"\n   Current Warp: {self.current_warp.name} ({self.current_warp.value})")
        print(f"   Mode: {config.name}")
        print(f"   Description: {config.description}")
        print(f"\n   Resource Allocation:")
        print(f"      Local:        {config.local_percent*100:.0f}%")
        print(f"      Subscription: {config.subscription_percent*100:.0f}%")
        print(f"      Cloud:         {config.cloud_percent*100:.0f}%")
        print(f"\n   Estimated Monthly Cost: ${config.estimated_monthly_cost:.2f}")
        print(f"   Sustainability: {config.sustainability.upper()}")
        print(f"   Parallel Processing: {'Enabled' if config.use_parallel else 'Disabled'}")
        if config.max_cloud_requests_per_day:
            print(f"   Max Cloud Requests/Day: {config.max_cloud_requests_per_day}")
        print("\n" + "=" * 80)

    def print_all_warp_levels(self):
        """Print all available warp factor levels"""
        print("\n" + "=" * 80)
        print("⚡ ULTRON WARP FACTOR SCALE")
        print("                    -LUM THE MODERN")
        print("=" * 80)
        print("\n┌" + "─" * 78 + "┐")
        print("│" + f"{'Warp':<8} │ {'Name':<25} │ {'Cost/Mo':<12} │ {'Sustainability':<20}" + "│")
        print("├" + "─" * 78 + "┤")

        for warp in WarpFactor:
            config = self.configs[warp]
            current = "← CURRENT" if warp == self.current_warp else ""
            print(f"│  {warp.value:<6} │ {config.name:<25} │ ${config.estimated_monthly_cost:<10.2f} │ {config.sustainability:<20} {current}" + "│")

        print("└" + "─" * 78 + "┘")
        print("\n💡 RECOMMENDATION: Warp 9 (Smart Hybrid) - Optimal balance of capability and cost")
        print("=" * 80)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="ULTRON Warp Factor Controller")
    parser.add_argument("--status", action="store_true", help="Show current warp factor")
    parser.add_argument("--list", action="store_true", help="List all warp factor levels")
    parser.add_argument("--set", type=int, help="Set warp factor (1-11)")
    parser.add_argument("--test", type=str, help="Test routing decision for a prompt")

    args = parser.parse_args()

    controller = ULTRONWarpFactorController()

    if args.set:
        try:
            warp = WarpFactor(args.set)
            controller.set_warp_factor(warp)
            controller.print_warp_status()
        except ValueError as e:
            print(f"❌ Error: {e}")
            print(f"Valid warp factors: 1-11")

    elif args.test:
        decision = controller.get_routing_decision(args.test)
        print(f"\n🎯 ROUTING DECISION (Warp {decision['warp_factor']}):")
        print(f"   Target: {decision['target']}")
        print(f"   Model: {decision['model']}")
        print(f"   Est. Cost: ${decision['estimated_cost']:.6f} per request")
        print(f"   Reasoning: {decision['reasoning']}")

    elif args.list:
        controller.print_all_warp_levels()

    else:
        controller.print_warp_status()


if __name__ == "__main__":


    main()