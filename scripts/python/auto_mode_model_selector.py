#!/usr/bin/env python3
"""
@auto Mode Model Selector
<COMPANY_NAME> LLC

Selects optimal model from full spectrum (local → cloud):
- Local models (KAIJU IRON LEGION, local Ollama, etc.)
- Cloud models (Anthropic, OpenAI, etc.)
- Hybrid combinations
- Multi-modal models

INTEGRATED WITH CLOUD AI PROVIDER TRACKER:
- Uses learned provider performance for selection
- Learns best provider for each job type

@JARVIS @MARVIN @SYPHON #DECISIONING
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from universal_logging_wrapper import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

from auto_mode_decision_tree import ModelSpectrum, Modality, RequestAnalysis

# Import Cloud AI Provider Tracker
try:
    from cloud_ai_provider_tracker import (
        CloudAIProviderTracker,
        ProviderType,
        TaskCategory,
        get_provider_tracker
    )
    PROVIDER_TRACKER_AVAILABLE = True
except ImportError:
    PROVIDER_TRACKER_AVAILABLE = False
    logger = get_logger("AutoModeModelSelector")
    logger.warning("⚠️  CloudAIProviderTracker not available")

logger = get_logger("AutoModeModelSelector")


class ModelProvider(Enum):
    """Model providers (local and cloud)"""
    # Local AI Providers
    ULTRON = "ultron"  # ULTRON Hybrid Cluster
    ULTRON_LOCAL = "ultron_local"  # Local ULTRON only
    KAIJU_IRON_LEGION = "kaiju_iron_legion"  # KAIJU Iron Legion
    IRON_LEGION = "iron_legion"  # Iron Legion Cluster
    IRON_LEGION_ROUTER = "iron_legion_router"  # Iron Legion Router
    LOAD_BALANCER = "load_balancer"  # Load Balancer
    LOCAL_CLUSTER = "local_cluster"  # Generic Local Cluster
    DOCKER_OLLAMA = "docker_ollama"  # Docker Ollama

    # Cloud AI Providers
    ANTHROPIC_CLAUDE = "anthropic_claude"
    OPENAI_GPT4 = "openai_gpt4"
    OPENAI_GPT35 = "openai_gpt35"
    AZURE_OPENAI = "azure_openai"
    GROK = "grok"  # Grok (free tier preferred)


@dataclass
class ModelSelection:
    """Model selection result"""
    primary: ModelProvider
    fallback: Optional[ModelProvider]
    hybrid: Optional[Dict[str, ModelProvider]]
    reason: str
    confidence: float


class AutoModeModelSelector:
    """
    Select optimal model from full spectrum

    INTEGRATED WITH CLOUD AI PROVIDER TRACKER:
    - Uses learned provider performance for selection
    - Learns best provider for each job type
    """

    def __init__(self):
        self.logger = logger

        # Initialize Cloud AI Provider Tracker
        self.provider_tracker = None
        if PROVIDER_TRACKER_AVAILABLE:
            try:
                self.provider_tracker = get_provider_tracker()
                self.logger.info("✅ Cloud AI Provider Tracker integrated")
            except Exception as e:
                self.logger.warning(f"⚠️  Provider tracker init error: {e}")

        # Initialize AI Agent Live Monitor for transparency
        try:
            from ai_agent_live_monitor import get_live_monitor
            self.live_monitor = get_live_monitor()
            self.logger.info("✅ AI Agent Live Monitor integrated for transparency")
        except Exception as e:
            self.logger.warning(f"⚠️  Live monitor init error: {e}")
            self.live_monitor = None

        self.logger.info("✅ Auto Mode Model Selector initialized")

    def select(self, decision: Any, analysis: RequestAnalysis) -> ModelSelection:
        """Select model based on decision and analysis"""

        spectrum = decision.model_spectrum

        if spectrum == ModelSpectrum.LOCAL_ONLY:
            selection = self._select_local(analysis)
        elif spectrum == ModelSpectrum.CLOUD_ONLY:
            selection = self._select_cloud(analysis)
        else:  # HYBRID
            selection = self._select_hybrid(analysis)

        # Update live monitor with selected model
        if self.live_monitor:
            try:
                task_description = f"Model Selection: {selection.primary.value} ({selection.reason})"
                self.live_monitor.set_current_task(task_description)
            except Exception as e:
                self.logger.warning(f"⚠️  Live monitor update error: {e}")

        # Register with model transparency system
        try:
            from ai_model_transparency_system import (
                get_model_transparency,
                ModelType,
                register_active_model
            )
            transparency = get_model_transparency()

            # Determine model type
            model_type = ModelType.LOCAL if selection.primary.value in [
                "ultron", "ultron_local", "kaiju_iron_legion", "iron_legion",
                "iron_legion_router", "load_balancer", "local_cluster", "docker_ollama"
            ] else ModelType.CLOUD

            # Register for transparency
            transparency.register_model_selection(
                provider=selection.primary.value.upper().replace("_", " "),
                model_name=selection.primary.value,
                model_type=model_type,
                selection_reason=selection.reason,
                confidence=selection.confidence
            )
        except ImportError:
            self.logger.warning("⚠️  Model transparency system not available")
        except Exception as e:
            self.logger.warning(f"⚠️  Model transparency registration error: {e}")

        return selection

    def _select_local(self, analysis: RequestAnalysis) -> ModelSelection:
        """
        Select local model

        Uses Cloud AI Provider Tracker to learn best local provider for job type
        Priority: ULTRON > Iron Legion > Router > Load Balancer > Local Cluster > Docker Ollama
        """
        # Map intent to task category for provider tracker
        intent_to_category = {
            "fix": TaskCategory.DEBUGGING,
            "create": TaskCategory.CODE_GENERATION,
            "analyze": TaskCategory.ANALYSIS,
            "general": TaskCategory.QUESTION_ANSWERING
        }

        task_category = intent_to_category.get(analysis.intent, TaskCategory.QUESTION_ANSWERING)

        # Use provider tracker to get best local provider if available
        # MEASURE TWICE, CUT ONCE: Use least powerful sufficient + cheapest
        best_provider_type = None
        if self.provider_tracker:
            try:
                # Get best provider, but filter for local providers only
                local_providers = [
                    ProviderType.ULTRON,
                    ProviderType.IRON_LEGION,
                    ProviderType.KAIJU_IRON_LEGION,
                    ProviderType.ULTRON_LOCAL,
                    ProviderType.IRON_LEGION_ROUTER
                ]

                # Get best provider using intelligent selection (least powerful + cheapest)
                best = self.provider_tracker.get_best_provider_for_job(
                    task_category,
                    min_confidence=0.6,
                    use_least_powerful=True,  # Always use least powerful sufficient
                    prioritize_cost=True  # Always prioritize cost
                )

                # Filter to local providers only
                if best and best in local_providers:
                    best_provider_type = best
                    self.logger.info(f"   🎯 Provider tracker recommends (least powerful + cheapest): {best_provider_type.value}")
                else:
                    # Fallback: Get recommendations and filter for local
                    recs = self.provider_tracker.get_provider_recommendations(task_category, top_n=5)
                    for rec in recs:
                        if rec["provider"] in local_providers:
                            best_provider_type = rec["provider"]
                            self.logger.info(f"   🎯 Provider tracker recommends local: {best_provider_type.value}")
                            break
            except Exception as e:
                self.logger.warning(f"⚠️  Provider tracker error: {e}")

        # Map ProviderType to ModelProvider
        provider_mapping = {
            ProviderType.ULTRON: ModelProvider.ULTRON,
            ProviderType.IRON_LEGION: ModelProvider.IRON_LEGION,
            ProviderType.KAIJU_IRON_LEGION: ModelProvider.KAIJU_IRON_LEGION,
            ProviderType.ULTRON_LOCAL: ModelProvider.ULTRON_LOCAL,
            ProviderType.IRON_LEGION_ROUTER: ModelProvider.IRON_LEGION_ROUTER
        }

        # Use learned provider if available, otherwise use heuristics
        if best_provider_type and best_provider_type in provider_mapping:
            primary = provider_mapping[best_provider_type]
            fallback = ModelProvider.IRON_LEGION_ROUTER if primary != ModelProvider.IRON_LEGION_ROUTER else ModelProvider.ULTRON

            return ModelSelection(
                primary=primary,
                fallback=fallback,
                hybrid=None,
                reason=f"Learned best local provider for {task_category.value}: {best_provider_type.value}",
                confidence=0.90
            )

        # Fallback to heuristics if no learned provider
        # Priority: ULTRON > Iron Legion > Router > Load Balancer
        if analysis.complexity == "high":
            return ModelSelection(
                primary=ModelProvider.ULTRON,
                fallback=ModelProvider.IRON_LEGION,
                hybrid=None,
                reason="High complexity requires ULTRON hybrid cluster",
                confidence=0.90
            )
        elif analysis.speed_requirement == "critical":
            return ModelSelection(
                primary=ModelProvider.IRON_LEGION_ROUTER,
                fallback=ModelProvider.LOAD_BALANCER,
                hybrid=None,
                reason="Critical speed requires fast routing",
                confidence=0.85
            )
        else:
            return ModelSelection(
                primary=ModelProvider.ULTRON,
                fallback=ModelProvider.IRON_LEGION,
                hybrid=None,
                reason="Default to ULTRON for balanced local performance",
                confidence=0.85
            )

    def _select_cloud(self, analysis: RequestAnalysis) -> ModelSelection:
        """
        Select cloud model

        Uses Cloud AI Provider Tracker to learn best provider for job type
        """
        # Map intent to task category for provider tracker
        intent_to_category = {
            "fix": TaskCategory.DEBUGGING,
            "create": TaskCategory.CODE_GENERATION,
            "analyze": TaskCategory.ANALYSIS,
            "general": TaskCategory.QUESTION_ANSWERING
        }

        task_category = intent_to_category.get(analysis.intent, TaskCategory.QUESTION_ANSWERING)

        # Use provider tracker to get best provider if available
        # MEASURE TWICE, CUT ONCE: Use least powerful sufficient + cheapest
        best_provider_type = None
        if self.provider_tracker:
            try:
                best_provider_type = self.provider_tracker.get_best_provider_for_job(
                    task_category,
                    min_confidence=0.6,
                    use_least_powerful=True,  # Always use least powerful sufficient
                    prioritize_cost=True  # Always prioritize cost
                )
                if best_provider_type:
                    self.logger.info(f"   🎯 Provider tracker recommends (least powerful + cheapest): {best_provider_type.value}")
            except Exception as e:
                self.logger.warning(f"⚠️  Provider tracker error: {e}")

        # Map ProviderType to ModelProvider (cloud only)
        # COST OPTIMIZATION: Priority order (cheapest first)
        # Grok (free) > GPT-3.5 (cheap) > Claude (medium) > GPT-4 (expensive)
        provider_mapping = {
            ProviderType.OPENAI: ModelProvider.OPENAI_GPT4,
            ProviderType.ANTHROPIC: ModelProvider.ANTHROPIC_CLAUDE,
            ProviderType.AZURE_OPENAI: ModelProvider.AZURE_OPENAI,
            ProviderType.GOOGLE: ModelProvider.GROK,  # Grok preferred (free tier)
        }

        # COST OPTIMIZATION: Prefer Grok (free tier) if no specific provider recommended
        # Grok is the cheapest cloud option (free tier)
        if best_provider_type is None or best_provider_type not in provider_mapping:
            # No specific recommendation - use Grok (cheapest/free)
            return ModelSelection(
                primary=ModelProvider.GROK,
                fallback=ModelProvider.OPENAI_GPT35,
                hybrid=None,
                reason=f"Cost optimization: Using Grok (free tier, cheapest cloud option) for {task_category.value}",
                confidence=0.85
            )

        # Use learned provider if available, otherwise use heuristics
        # COST OPTIMIZATION: Prefer Grok (free) > GPT-3.5 (cheap) > Claude (medium) > GPT-4 (expensive)
        if best_provider_type and best_provider_type in provider_mapping:
            primary = provider_mapping[best_provider_type]
            fallback = ModelProvider.ANTHROPIC_CLAUDE if primary != ModelProvider.ANTHROPIC_CLAUDE else ModelProvider.OPENAI_GPT4

            return ModelSelection(
                primary=primary,
                fallback=fallback,
                hybrid=None,
                reason=f"Learned best provider for {task_category.value}: {best_provider_type.value} (cost optimized)",
                confidence=0.90
            )

        # Fallback to heuristics if no learned provider
        # COST OPTIMIZATION: Use cheapest capable model
        if analysis.complexity == "high":
            # High complexity - need capable model, but prefer cheaper options
            return ModelSelection(
                primary=ModelProvider.ANTHROPIC_CLAUDE,  # Claude is cheaper than GPT-4
                fallback=ModelProvider.OPENAI_GPT4,
                hybrid=None,
                reason="High complexity - using Claude (cost optimized vs GPT-4)",
                confidence=0.90
            )
        elif analysis.speed_requirement == "critical":
            # Critical speed - prefer Grok (free) or GPT-3.5 (cheap)
            return ModelSelection(
                primary=ModelProvider.GROK,  # Grok free tier preferred
                fallback=ModelProvider.OPENAI_GPT35,
                hybrid=None,
                reason="Critical speed - using Grok (free tier, cost optimized)",
                confidence=0.85
            )
        else:
            # Default: Use Grok (free tier) or cheapest option
            return ModelSelection(
                primary=ModelProvider.GROK,  # Grok free tier preferred
                fallback=ModelProvider.OPENAI_GPT35,
                hybrid=None,
                reason="Default - using Grok (free tier, cost optimized)",
                confidence=0.85
            )

    def _select_hybrid(self, analysis: RequestAnalysis) -> ModelSelection:
        """
        Select hybrid model combination

        Uses local-first approach: ULTRON/Iron Legion for most tasks, cloud for complex/escalated
        """
        # Map intent to task category
        intent_to_category = {
            "fix": TaskCategory.DEBUGGING,
            "create": TaskCategory.CODE_GENERATION,
            "analyze": TaskCategory.ANALYSIS,
            "general": TaskCategory.QUESTION_ANSWERING
        }

        task_category = intent_to_category.get(analysis.intent, TaskCategory.QUESTION_ANSWERING)

        # Use provider tracker to get best providers (local and cloud)
        # MEASURE TWICE, CUT ONCE: Use least powerful sufficient + cheapest
        best_local = None
        best_cloud = None

        if self.provider_tracker:
            try:
                # Get best local provider (least powerful + cheapest)
                local_providers = [
                    ProviderType.ULTRON,
                    ProviderType.IRON_LEGION,
                    ProviderType.KAIJU_IRON_LEGION
                ]

                # Find best local (least powerful sufficient + cheapest)
                for provider_type in local_providers:
                    if provider_type in self.provider_tracker.providers:
                        provider = self.provider_tracker.providers[provider_type]
                        if task_category in provider.job_performance:
                            perf = provider.job_performance[task_category]
                            if perf.overall_score >= 0.6:
                                best_local = provider_type
                                break

                # If no local found, try to get from recommendations
                if not best_local:
                    recs = self.provider_tracker.get_provider_recommendations(task_category, top_n=5)
                    for rec in recs:
                        if rec["provider"] in local_providers:
                            best_local = rec["provider"]
                            break

                # Get best cloud provider (least powerful sufficient + cheapest)
                best_cloud = self.provider_tracker.get_best_provider_for_job(
                    task_category,
                    min_confidence=0.6,
                    use_least_powerful=True,
                    prioritize_cost=True
                )

                # Ensure cloud provider is actually cloud
                cloud_providers = [
                    ProviderType.OPENAI,
                    ProviderType.ANTHROPIC,
                    ProviderType.AZURE_OPENAI,
                    ProviderType.GOOGLE
                ]
                if best_cloud and best_cloud not in cloud_providers:
                    best_cloud = None

            except Exception as e:
                self.logger.warning(f"⚠️  Provider tracker error: {e}")

        # Map providers
        local_mapping = {
            ProviderType.ULTRON: ModelProvider.ULTRON,
            ProviderType.IRON_LEGION: ModelProvider.IRON_LEGION,
            ProviderType.KAIJU_IRON_LEGION: ModelProvider.KAIJU_IRON_LEGION
        }
        cloud_mapping = {
            ProviderType.OPENAI: ModelProvider.OPENAI_GPT4,
            ProviderType.ANTHROPIC: ModelProvider.ANTHROPIC_CLAUDE,
            ProviderType.AZURE_OPENAI: ModelProvider.AZURE_OPENAI
        }

        # Use learned providers or defaults
        primary = local_mapping.get(best_local, ModelProvider.ULTRON) if best_local else ModelProvider.ULTRON
        fallback = cloud_mapping.get(best_cloud, ModelProvider.ANTHROPIC_CLAUDE) if best_cloud else ModelProvider.ANTHROPIC_CLAUDE

        return ModelSelection(
            primary=primary,
            fallback=fallback,
            hybrid={
                "simple": primary,  # Use local for simple tasks
                "complex": fallback  # Use cloud for complex tasks
            },
            reason=f"Hybrid: {primary.value} for simple, {fallback.value} for complex (learned from performance)",
            confidence=0.85
        )

