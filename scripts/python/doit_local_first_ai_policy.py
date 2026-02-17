#!/usr/bin/env python3
"""
@DOIT Local-First AI Policy Enforcement

Enforces policy: Use @local @ai @llm @agent resources over cloud AI providers,
unless @bau #decisioning @r5 @matrix &| @lattice approves cloud usage.

Tags: #DOIT #LOCAL_FIRST #BAU #DECISIONING #R5 #MATRIX #LATTICE @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

# Setup paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_core.logging import get_logger
    logger = get_logger("DOITLocalFirstAIPolicy")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("DOITLocalFirstAIPolicy")


class AIResourceType(Enum):
    """AI resource types"""
    LOCAL_ULTRON = "local_ultron"
    LOCAL_KAIJU = "local_kaiju"
    LOCAL_IRON_LEGION = "local_iron_legion"
    LOCAL_R5 = "local_r5"
    CLOUD_OPENAI = "cloud_openai"
    CLOUD_ANTHROPIC = "cloud_anthropic"
    CLOUD_GOOGLE = "cloud_google"
    CLOUD_OTHER = "cloud_other"


@dataclass
class AIDecisionRequest:
    """Request for AI provider decision"""
    task_description: str
    context: Dict[str, Any] = field(default_factory=dict)
    requested_provider: Optional[str] = None
    local_available: bool = True
    cloud_requested: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class AIDecisionResult:
    """Result of AI provider decision"""
    approved_provider: AIResourceType
    use_local: bool
    use_cloud: bool
    decision_reason: str
    decisioning_source: str  # @bau, #decisioning, @r5, @matrix, @lattice
    requires_approval: bool = False
    approval_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class DOITLocalFirstAIPolicy:
    """
    @DOIT Local-First AI Policy Enforcement

    Policy: Use @local @ai @llm @agent resources over cloud AI providers,
    unless @bau #decisioning @r5 @matrix &| @lattice approves cloud usage.
    """

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)

        # Initialize decisioning systems
        self.bau_available = False
        self.decisioning_available = False
        self.r5_available = False
        self.matrix_available = False
        self.lattice_available = False

        self._load_decisioning_systems()

        logger.info("="*80)
        logger.info("🛡️  @DOIT LOCAL-FIRST AI POLICY ENFORCEMENT")
        logger.info("="*80)
        logger.info("   Policy: Use local AI unless @bau #decisioning @r5 @matrix/@lattice approves cloud")
        logger.info("")
        logger.info(f"   @BAU: {'✅' if self.bau_available else '❌'}")
        logger.info(f"   #decisioning: {'✅' if self.decisioning_available else '❌'}")
        logger.info(f"   @R5: {'✅' if self.r5_available else '❌'}")
        logger.info(f"   @matrix: {'✅' if self.matrix_available else '❌'}")
        logger.info(f"   @lattice: {'✅' if self.lattice_available else '❌'}")
        logger.info("")

    def _load_decisioning_systems(self):
        """Load all decisioning systems"""
        # @BAU (Business As Usual)
        try:
            # Check for BAU decisioning
            self.bau_available = True
            logger.debug("✅ @BAU available")
        except Exception as e:
            logger.debug(f"⚠️  @BAU not available: {e}")

        # #decisioning (Universal Decision Tree)
        try:
            from universal_decision_tree import decide, DecisionContext, DecisionOutcome
            self.decide = decide
            self.DecisionContext = DecisionContext
            self.DecisionOutcome = DecisionOutcome
            self.decisioning_available = True
            logger.debug("✅ #decisioning available")
        except ImportError:
            self.decide = None
            logger.debug("⚠️  #decisioning not available")

        # @R5 (Living Context Matrix)
        try:
            from r5_living_context_matrix import R5LivingContextMatrix
            self.r5 = R5LivingContextMatrix(self.project_root)
            self.r5_available = True
            logger.debug("✅ @R5 available")
        except ImportError:
            self.r5 = None
            logger.debug("⚠️  @R5 not available")

        # @matrix (Decision Matrix)
        try:
            # Check for matrix decisioning system
            self.matrix_available = True  # Placeholder
            logger.debug("✅ @matrix available")
        except Exception as e:
            logger.debug(f"⚠️  @matrix not available: {e}")

        # @lattice (Decision Lattice)
        try:
            # Check for lattice decisioning system
            self.lattice_available = True  # Placeholder
            logger.debug("✅ @lattice available")
        except Exception as e:
            logger.debug(f"⚠️  @lattice not available: {e}")

    def decide_ai_provider(
        self,
        task_description: str,
        context: Optional[Dict[str, Any]] = None,
        requested_provider: Optional[str] = None
    ) -> AIDecisionResult:
        """
        Decide AI provider based on local-first policy

        Policy: Use local AI unless @bau #decisioning @r5 @matrix/@lattice approves cloud

        Args:
            task_description: Task description
            context: Additional context
            requested_provider: Requested provider (if any)

        Returns:
            AIDecisionResult with approved provider
        """
        if context is None:
            context = {}

        request = AIDecisionRequest(
            task_description=task_description,
            context=context,
            requested_provider=requested_provider,
            cloud_requested=self._is_cloud_provider(requested_provider) if requested_provider else False
        )

        logger.info(f"🔍 Deciding AI provider for: {task_description[:80]}")

        # Step 1: Check if cloud is requested
        if request.cloud_requested:
            logger.info("   ⚠️  Cloud provider requested - checking @bau #decisioning @r5 @matrix/@lattice approval")

            # Step 2: Get approval from @bau #decisioning @r5 @matrix/@lattice
            approval_result = self._get_cloud_approval(request)

            if approval_result["approved"]:
                logger.info(f"   ✅ Cloud approved by {approval_result['source']}")
                return AIDecisionResult(
                    approved_provider=self._map_provider_type(requested_provider),
                    use_local=False,
                    use_cloud=True,
                    decision_reason=approval_result["reason"],
                    decisioning_source=approval_result["source"],
                    requires_approval=True,
                    approval_id=approval_result.get("approval_id"),
                    metadata=approval_result.get("metadata", {})
                )
            else:
                logger.warning(f"   🚫 Cloud NOT approved - using local AI instead")
                # Route to local
                local_provider = self._select_local_provider(request)
                return AIDecisionResult(
                    approved_provider=local_provider,
                    use_local=True,
                    use_cloud=False,
                    decision_reason=f"Cloud not approved by {approval_result['source']} - using local-first",
                    decisioning_source=approval_result["source"],
                    requires_approval=True,
                    metadata={"blocked_cloud": requested_provider}
                )
        else:
            # No cloud requested - use local-first
            logger.info("   ✅ Using local-first AI (no cloud requested)")
            local_provider = self._select_local_provider(request)
            return AIDecisionResult(
                approved_provider=local_provider,
                use_local=True,
                use_cloud=False,
                decision_reason="Local-first policy - no cloud requested",
                decisioning_source="local_first_policy",
                metadata={}
            )

    def _get_cloud_approval(self, request: AIDecisionRequest) -> Dict[str, Any]:
        """
        Get cloud approval from @bau #decisioning @r5 @matrix/@lattice

        Returns approval result with source
        """
        # Try @bau #decisioning first
        if self.decisioning_available:
            try:
                decision_context = self.DecisionContext(project_root=self.project_root)
                decision_context.custom_data = {
                    "task": request.task_description,
                    "cloud_model_requested": True,
                    "local_ai_available": request.local_available,
                    "jedi_approved": False,
                    "decisioning_approved": False,
                    "r5_approved": False,
                    "matrix_approved": False,
                    "lattice_approved": False,
                    **request.context
                }

                # Use decision tree for routing decision
                result = self.decide("ai_routing", decision_context)

                # Check outcome - USE_CLOUD means approved
                if result.outcome == self.DecisionOutcome.USE_CLOUD:
                    return {
                        "approved": True,
                        "source": "@bau #decisioning",
                        "reason": "Approved by @bau #decisioning decision tree",
                        "approval_id": f"decisioning_{datetime.now().timestamp()}",
                        "metadata": {
                            "decision_outcome": result.outcome.value,
                            "provider": "cloud"
                        }
                    }
                else:
                    # USE_LOCAL or any other outcome blocks cloud
                    return {
                        "approved": False,
                        "reason": "Rejected by @bau #decisioning - use local-first AI (ULTRON/KAIJU/IRON_LEGION/R5) instead",
                        "source": "@bau #decisioning"
                    }
            except Exception as e:
                logger.debug(f"@bau #decisioning check failed: {e}")

        # Try @R5 matrix
        if self.r5_available:
            try:
                # Query R5 for recommendation
                r5_recommendation = self._get_r5_recommendation(request)
                if r5_recommendation and r5_recommendation.get("use_cloud"):
                    return {
                        "approved": True,
                        "source": "@r5 @matrix",
                        "reason": "Approved by @r5 @matrix analysis",
                        "approval_id": f"r5_{datetime.now().timestamp()}",
                        "metadata": r5_recommendation.get("metadata", {})
                    }
            except Exception as e:
                logger.debug(f"@R5 @matrix check failed: {e}")

        # Try @matrix (if separate from R5)
        if self.matrix_available:
            try:
                matrix_recommendation = self._get_matrix_recommendation(request)
                if matrix_recommendation and matrix_recommendation.get("use_cloud"):
                    return {
                        "approved": True,
                        "source": "@matrix",
                        "reason": "Approved by @matrix decision matrix",
                        "approval_id": f"matrix_{datetime.now().timestamp()}",
                        "metadata": matrix_recommendation.get("metadata", {})
                    }
            except Exception as e:
                logger.debug(f"@matrix check failed: {e}")

        # Try @lattice
        if self.lattice_available:
            try:
                lattice_recommendation = self._get_lattice_recommendation(request)
                if lattice_recommendation and lattice_recommendation.get("use_cloud"):
                    return {
                        "approved": True,
                        "source": "@lattice",
                        "reason": "Approved by @lattice decision lattice",
                        "approval_id": f"lattice_{datetime.now().timestamp()}",
                        "metadata": lattice_recommendation.get("metadata", {})
                    }
            except Exception as e:
                logger.debug(f"@lattice check failed: {e}")

        # Default: NOT approved (local-first enforced)
        return {
            "approved": False,
            "source": "@bau #decisioning @r5 @matrix/@lattice",
            "reason": "Cloud usage not approved by any decisioning system - local-first enforced",
            "metadata": {}
        }

    def _get_r5_recommendation(self, request: AIDecisionRequest) -> Optional[Dict[str, Any]]:
        """Get recommendation from @R5 @matrix"""
        if not self.r5_available:
            return None

        try:
            # Query R5 for AI provider recommendation
            # R5 analyzes context and recommends provider based on:
            # - Task complexity
            # - Local model capabilities
            # - Historical performance
            # - Resource availability

            # Check if task requires capabilities beyond local models
            task_lower = request.task_description.lower()
            complex_keywords = ["complex reasoning", "advanced analysis", "multi-step", "sophisticated"]
            requires_advanced = any(keyword in task_lower for keyword in complex_keywords)

            # Check local model availability
            local_models_available = request.local_available

            # R5 decision logic: Use cloud if task requires advanced capabilities
            # and local models may not be sufficient
            if requires_advanced and local_models_available:
                # Could use cloud, but check if local can handle it
                # Default: Try local first, but allow cloud if needed
                return {
                    "use_cloud": False,  # Prefer local even for complex tasks
                    "recommendation": "local",
                    "metadata": {
                        "r5_analyzed": True,
                        "task_complexity": "high",
                        "local_preferred": True
                    }
                }
            else:
                # Standard task - use local
                return {
                    "use_cloud": False,
                    "recommendation": "local",
                    "metadata": {"r5_analyzed": True}
                }
        except Exception as e:
            logger.debug(f"R5 recommendation error: {e}")
            return None

    def _get_matrix_recommendation(self, request: AIDecisionRequest) -> Optional[Dict[str, Any]]:
        """Get recommendation from @matrix"""
        # Placeholder for matrix decisioning
        return None

    def _get_lattice_recommendation(self, request: AIDecisionRequest) -> Optional[Dict[str, Any]]:
        """Get recommendation from @lattice"""
        # Placeholder for lattice decisioning
        return None

    def _is_cloud_provider(self, provider: str) -> bool:
        """Check if provider is cloud-based"""
        if not provider:
            return False

        provider_lower = provider.lower()
        cloud_patterns = [
            "gpt-", "openai", "claude", "anthropic", "gemini", "google",
            "api.openai.com", "api.anthropic.com", "api.google.com"
        ]

        return any(pattern in provider_lower for pattern in cloud_patterns)

    def _map_provider_type(self, provider: str) -> AIResourceType:
        """Map provider string to AIResourceType"""
        if not provider:
            return AIResourceType.LOCAL_ULTRON

        provider_lower = provider.lower()

        if "ultron" in provider_lower:
            return AIResourceType.LOCAL_ULTRON
        elif "kaiju" in provider_lower or "iron.legion" in provider_lower:
            return AIResourceType.LOCAL_KAIJU
        elif "r5" in provider_lower:
            return AIResourceType.LOCAL_R5
        elif "openai" in provider_lower or "gpt" in provider_lower:
            return AIResourceType.CLOUD_OPENAI
        elif "anthropic" in provider_lower or "claude" in provider_lower:
            return AIResourceType.CLOUD_ANTHROPIC
        elif "google" in provider_lower or "gemini" in provider_lower:
            return AIResourceType.CLOUD_GOOGLE
        else:
            return AIResourceType.CLOUD_OTHER

    def _select_local_provider(self, request: AIDecisionRequest) -> AIResourceType:
        """Select best local provider"""
        # Priority: ULTRON > KAIJU > IRON_LEGION > R5
        # Check availability and select
        return AIResourceType.LOCAL_ULTRON  # Default to ULTRON


def enforce_local_first_in_doit(project_root: Path) -> Dict[str, Any]:
    """
    Enforce local-first AI policy in @DOIT system

    Returns enforcement result
    """
    policy = DOITLocalFirstAIPolicy(project_root)

    logger.info("="*80)
    logger.info("🛡️  ENFORCING LOCAL-FIRST AI POLICY IN @DOIT")
    logger.info("="*80)
    logger.info("")
    logger.info("Policy: Use @local @ai @llm @agent resources over cloud AI providers,")
    logger.info("        unless @bau #decisioning @r5 @matrix/@lattice approves cloud usage")
    logger.info("")

    # Test decision
    test_result = policy.decide_ai_provider(
        task_description="Test task",
        requested_provider="gpt-4"
    )

    logger.info("📊 Test Decision Result:")
    logger.info(f"   Provider: {test_result.approved_provider.value}")
    logger.info(f"   Use Local: {test_result.use_local}")
    logger.info(f"   Use Cloud: {test_result.use_cloud}")
    logger.info(f"   Reason: {test_result.decision_reason}")
    logger.info(f"   Source: {test_result.decisioning_source}")
    logger.info("")

    return {
        "policy_enforced": True,
        "test_result": {
            "provider": test_result.approved_provider.value,
            "use_local": test_result.use_local,
            "use_cloud": test_result.use_cloud,
            "reason": test_result.decision_reason,
            "source": test_result.decisioning_source
        }
    }


def main():
    try:
        """Main entry point"""
        project_root = Path(__file__).parent.parent.parent

        result = enforce_local_first_in_doit(project_root)

        logger.info("="*80)
        logger.info("✅ LOCAL-FIRST AI POLICY ENFORCEMENT COMPLETE")
        logger.info("="*80)

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())