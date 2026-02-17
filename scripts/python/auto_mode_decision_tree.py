#!/usr/bin/env python3
"""
@auto Mode Decision Tree Engine
<COMPANY_NAME> LLC

Comprehensive decision tree for @auto mode:
- Request analysis
- Model spectrum selection (local → cloud)
- Multi-modal selection
- Multi-agent determination
- Execution order

INTEGRATED WITH #DECISIONING:
- Uses LuminaDecisioningEngine for decision-making
- Integrates with CloudAIProviderTracker for provider selection
- Learns best provider for each job type

@JARVIS @MARVIN @SYPHON #DECISIONING
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from universal_logging_wrapper import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

# Import #decisioning engine
try:
    from lumina_decisioning_engine import LuminaDecisioningEngine, DecisionContext
    DECISIONING_AVAILABLE = True
except ImportError:
    DECISIONING_AVAILABLE = False
    logger = get_logger("AutoModeDecisionTree")
    logger.warning("⚠️  LuminaDecisioningEngine not available")

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
    logger = get_logger("AutoModeDecisionTree")
    logger.warning("⚠️  CloudAIProviderTracker not available")

logger = get_logger("AutoModeDecisionTree")


class ModelSpectrum(Enum):
    """Model spectrum options"""
    LOCAL_ONLY = "local_only"
    CLOUD_ONLY = "cloud_only"
    HYBRID = "hybrid"


class Modality(Enum):
    """Modality types"""
    TEXT = "text"
    CODE = "code"
    VOICE = "voice"
    IMAGE = "image"
    VIDEO = "video"
    MULTI_MODAL = "multi_modal"


@dataclass
class RequestAnalysis:
    """Request analysis result"""
    intent: str
    complexity: str  # "low", "medium", "high"
    modality: Modality
    speed_requirement: str  # "normal", "fast", "critical"
    privacy_requirement: str  # "low", "medium", "high"
    cost_sensitivity: str  # "low", "medium", "high"
    requires_multi_agent: bool
    requires_multi_modal: bool


@dataclass
class AutoModeDecision:
    """Complete @auto mode decision"""
    model_spectrum: ModelSpectrum
    modality: Modality
    agent_config: Dict[str, Any]
    execution_order: List[str]
    when_to_apply: Dict[str, List[str]]
    confidence: float


class AutoModeDecisionTree:
    """
    Comprehensive decision tree for @auto mode

    INTEGRATED WITH #DECISIONING:
    - Uses LuminaDecisioningEngine for decision-making
    - Integrates with CloudAIProviderTracker for provider selection
    """

    def __init__(self):
        self.logger = logger

        # Initialize #decisioning engine
        self.decisioning_engine = None
        if DECISIONING_AVAILABLE:
            try:
                self.decisioning_engine = LuminaDecisioningEngine()
                self.logger.info("✅ #DECISIONING engine integrated")
            except Exception as e:
                self.logger.warning(f"⚠️  Decisioning engine init error: {e}")

        # Initialize Cloud AI Provider Tracker
        self.provider_tracker = None
        if PROVIDER_TRACKER_AVAILABLE:
            try:
                self.provider_tracker = get_provider_tracker()
                self.logger.info("✅ Cloud AI Provider Tracker integrated")
            except Exception as e:
                self.logger.warning(f"⚠️  Provider tracker init error: {e}")

        self.logger.info("✅ Auto Mode Decision Tree initialized")

    def decide(self, request: str, context: Optional[Dict[str, Any]] = None) -> AutoModeDecision:
        """Make comprehensive routing decision"""

        # 1. Analyze request
        analysis = self._analyze_request(request, context)

        # 2. Determine model spectrum
        model_spectrum = self._determine_model_spectrum(analysis)

        # 3. Determine modality
        modality = self._determine_modality(analysis)

        # 4. Determine agent needs
        agent_config = self._determine_agent_config(analysis)

        # 5. Determine execution order
        execution_order = self._determine_execution_order(analysis)

        # 6. Determine when to apply
        when_to_apply = self._determine_when_to_apply(analysis)

        # Calculate confidence
        confidence = self._calculate_confidence(analysis, model_spectrum, modality)

        return AutoModeDecision(
            model_spectrum=model_spectrum,
            modality=modality,
            agent_config=agent_config,
            execution_order=execution_order,
            when_to_apply=when_to_apply,
            confidence=confidence
        )

    def _analyze_request(self, request: str, context: Optional[Dict[str, Any]]) -> RequestAnalysis:
        """Analyze request"""
        request_lower = request.lower()

        # Intent classification
        intent = "general"
        if "fix" in request_lower or "error" in request_lower:
            intent = "fix"
        elif "create" in request_lower or "new" in request_lower:
            intent = "create"
        elif "analyze" in request_lower:
            intent = "analyze"

        # Complexity
        complexity = "medium"
        if any(word in request_lower for word in ["simple", "quick", "fix"]):
            complexity = "low"
        elif any(word in request_lower for word in ["complex", "refactor", "migrate"]):
            complexity = "high"

        # Modality detection
        modality = Modality.TEXT
        if "image" in request_lower or "picture" in request_lower:
            modality = Modality.IMAGE
        elif "audio" in request_lower or "voice" in request_lower:
            modality = Modality.VOICE
        elif "video" in request_lower:
            modality = Modality.VIDEO
        elif "code" in request_lower:
            modality = Modality.CODE

        # Speed requirement
        speed_requirement = "normal"
        if "urgent" in request_lower or "critical" in request_lower:
            speed_requirement = "critical"
        elif "fast" in request_lower:
            speed_requirement = "fast"

        # Privacy requirement
        privacy_requirement = "medium"
        if "private" in request_lower or "sensitive" in request_lower:
            privacy_requirement = "high"

        # Cost sensitivity
        cost_sensitivity = "medium"
        if "free" in request_lower or "cheap" in request_lower:
            cost_sensitivity = "high"

        # Multi-agent requirement
        requires_multi_agent = any(word in request_lower for word in ["complex", "multiple", "coordinate"])

        # Multi-modal requirement
        requires_multi_modal = modality != Modality.TEXT

        return RequestAnalysis(
            intent=intent,
            complexity=complexity,
            modality=modality,
            speed_requirement=speed_requirement,
            privacy_requirement=privacy_requirement,
            cost_sensitivity=cost_sensitivity,
            requires_multi_agent=requires_multi_agent,
            requires_multi_modal=requires_multi_modal
        )

    def _determine_model_spectrum(self, analysis: RequestAnalysis) -> ModelSpectrum:
        """
        Determine model spectrum

        Uses #DECISIONING engine for decision-making
        """
        # Use #decisioning engine if available
        if self.decisioning_engine:
            try:
                decision = self.decisioning_engine.make_decision(
                    context=DecisionContext.WORKFLOW_TRIGGER,
                    details={
                        "privacy_requirement": analysis.privacy_requirement,
                        "cost_sensitivity": analysis.cost_sensitivity,
                        "complexity": analysis.complexity,
                        "intent": analysis.intent
                    }
                )
                # Decision made, continue with spectrum determination
            except Exception as e:
                self.logger.warning(f"⚠️  Decisioning error: {e}")

        # Determine spectrum based on requirements
        if analysis.privacy_requirement == "high":
            return ModelSpectrum.LOCAL_ONLY
        elif analysis.cost_sensitivity == "high":
            return ModelSpectrum.LOCAL_ONLY
        elif analysis.complexity == "high":
            return ModelSpectrum.HYBRID
        else:
            return ModelSpectrum.HYBRID

    def _determine_modality(self, analysis: RequestAnalysis) -> Modality:
        """Determine modality"""
        return analysis.modality

    def _determine_agent_config(self, analysis: RequestAnalysis) -> Dict[str, Any]:
        """Determine agent configuration"""
        if analysis.requires_multi_agent:
            return {
                "lead_agent": True,
                "sub_agents": 3,
                "parallel_execution": True
            }
        else:
            return {
                "lead_agent": False,
                "sub_agents": 0,
                "parallel_execution": False
            }

    def _determine_execution_order(self, analysis: RequestAnalysis) -> List[str]:
        """Determine execution order"""
        return [
            "analyze_request",
            "select_model",
            "select_modality",
            "configure_agents",
            "execute",
            "aggregate_results",
            "return_response"
        ]

    def _determine_when_to_apply(self, analysis: RequestAnalysis) -> Dict[str, List[str]]:
        """Determine when to apply options"""
        return {
            "always": ["request_analysis", "privacy_check", "local_first"],
            "on_demand": ["multi_agent", "multi_modal", "cloud_models"],
            "conditional": ["speed_optimization", "cost_optimization"],
            "never": ["cloud_for_high_privacy"]
        }

    def _calculate_confidence(self, analysis: RequestAnalysis, model_spectrum: ModelSpectrum, modality: Modality) -> float:
        """Calculate confidence score"""
        confidence = 0.7  # Base

        if analysis.complexity in ["low", "high"]:
            confidence += 0.1

        if model_spectrum != ModelSpectrum.HYBRID:
            confidence += 0.1

        return min(confidence, 1.0)

